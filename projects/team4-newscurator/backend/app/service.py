from __future__ import annotations

from datetime import datetime, timezone
from difflib import SequenceMatcher

from backend.app.catalog import SOURCE_BY_ID, TOPIC_BY_ID, source_labels, topic_keywords, topic_labels
from backend.app.db import Repository
from backend.app.models import Article, Briefing, BriefingHistoryItem, BriefingRequest, BriefingStats, FetchReport
from backend.app.news_client import NewsClient
from backend.app.summarizer import Summarizer


class ValidationError(ValueError):
    pass


class BriefingService:
    def __init__(
        self,
        *,
        news_client: NewsClient,
        summarizer: Summarizer,
        repository: Repository,
    ) -> None:
        self.news_client = news_client
        self.summarizer = summarizer
        self.repository = repository

    def create_briefing(self, request: BriefingRequest) -> Briefing:
        self._validate_request(request)
        custom_keywords = self._custom_keywords(request)
        exclude_keywords = self._exclude_keywords(request)
        raw_articles, news_notices, used_sample_data, fetch_report = self.news_client.fetch(
            sources=request.sources,
            topics=request.topics,
            custom_keywords=custom_keywords,
            date_range=request.date_range,
            limit=request.limit,
        )
        filtered_articles = self._filter_articles(raw_articles, request.topics, custom_keywords, exclude_keywords)
        deduped_articles = self._dedupe_articles(filtered_articles)
        ranked_articles = self._rank_articles(deduped_articles, request.topics, custom_keywords)[: request.limit]
        stats = self._stats(
            request=request,
            fetch_report=fetch_report,
            matched_count=len(filtered_articles),
            deduped_count=len(deduped_articles),
            selected_count=len(ranked_articles),
        )

        if not ranked_articles:
            return Briefing(
                title="관련 뉴스가 없습니다",
                generated_at=datetime.now(),
                source_labels=source_labels(request.sources),
                topic_labels=topic_labels(request.topics),
                custom_keywords=custom_keywords,
                exclude_keywords=exclude_keywords,
                date_range=request.date_range,
                common_topics=[],
                articles=[],
                notices=["관련 뉴스가 없습니다."],
                stats=stats,
                used_sample_data=used_sample_data,
            )

        focus_labels = self._focus_labels(request, custom_keywords)
        summarized, common_topics, summary_notices = self.summarizer.summarize(
            ranked_articles, focus_labels
        )
        briefing = Briefing(
            title=self._briefing_title(request),
            generated_at=datetime.now(),
            source_labels=source_labels(request.sources),
            topic_labels=topic_labels(request.topics),
            custom_keywords=custom_keywords,
            exclude_keywords=exclude_keywords,
            date_range=request.date_range,
            common_topics=common_topics,
            articles=summarized,
            notices=news_notices + summary_notices,
            stats=stats,
            used_sample_data=used_sample_data,
        )
        self.repository.save_articles(summarized)
        self.repository.save_briefing(
            sources=request.sources,
            topics=request.topics,
            date_range=request.date_range,
            briefing=briefing,
        )
        return briefing

    def list_history(self, limit: int = 8) -> list[BriefingHistoryItem]:
        rows = self.repository.latest_briefings(limit=limit)
        items: list[BriefingHistoryItem] = []
        for row in rows:
            briefing = Briefing.model_validate_json(row["result_json"])
            items.append(
                BriefingHistoryItem(
                    id=row["id"],
                    title=briefing.title,
                    created_at=row["created_at"],
                    generated_at=briefing.generated_at,
                    source_labels=briefing.source_labels,
                    topic_labels=briefing.topic_labels,
                    custom_keywords=briefing.custom_keywords,
                    exclude_keywords=briefing.exclude_keywords,
                    date_range=briefing.date_range,
                    article_count=len(briefing.articles),
                    used_sample_data=briefing.used_sample_data,
                )
            )
        return items

    def get_briefing(self, briefing_id: int) -> Briefing | None:
        row = self.repository.get_briefing(briefing_id)
        if not row:
            return None
        return Briefing.model_validate_json(row["result_json"])

    def _validate_request(self, request: BriefingRequest) -> None:
        if not request.sources:
            raise ValidationError("언론사를 하나 이상 선택해주세요.")
        if not request.topics and not self._custom_keywords(request):
            raise ValidationError("관심 분야나 추가 키워드를 하나 이상 선택해주세요.")

        invalid_sources = [source for source in request.sources if source not in SOURCE_BY_ID]
        invalid_topics = [topic for topic in request.topics if topic not in TOPIC_BY_ID]
        if invalid_sources:
            raise ValidationError(f"지원하지 않는 언론사입니다: {', '.join(invalid_sources)}")
        if invalid_topics:
            raise ValidationError(f"지원하지 않는 관심 분야입니다: {', '.join(invalid_topics)}")

    def _custom_keywords(self, request: BriefingRequest) -> list[str]:
        return self._clean_keywords(request.custom_keywords)

    def _exclude_keywords(self, request: BriefingRequest) -> list[str]:
        return self._clean_keywords(request.exclude_keywords)

    def _clean_keywords(self, values: list[str]) -> list[str]:
        keywords: list[str] = []
        for keyword in values:
            normalized = " ".join(keyword.strip().split())
            if normalized and normalized not in keywords:
                keywords.append(normalized)
            if len(keywords) == 20:
                break
        return keywords

    def _focus_labels(self, request: BriefingRequest, custom_keywords: list[str]) -> list[str]:
        return topic_labels(request.topics) + custom_keywords

    def _effective_keywords(self, topics: list[str], custom_keywords: list[str]) -> list[str]:
        keywords = topic_keywords(topics) + custom_keywords
        return list(dict.fromkeys(keyword for keyword in keywords if keyword.strip()))

    def _filter_articles(
        self, articles: list[Article], topics: list[str], custom_keywords: list[str], exclude_keywords: list[str]
    ) -> list[Article]:
        keywords = [keyword.lower() for keyword in self._effective_keywords(topics, custom_keywords)]
        excluded = [keyword.lower() for keyword in exclude_keywords]
        allowed_articles = []
        for article in articles:
            haystack = f"{article.title} {article.description or ''}".lower()
            if excluded and any(keyword in haystack for keyword in excluded):
                continue
            allowed_articles.append(article)

        if not keywords:
            return allowed_articles

        matched: list[Article] = []
        for article in allowed_articles:
            haystack = f"{article.title} {article.description or ''}".lower()
            if any(keyword in haystack for keyword in keywords):
                matched.append(article)

        return matched

    def _dedupe_articles(self, articles: list[Article]) -> list[Article]:
        unique: list[Article] = []
        seen_urls: set[str] = set()
        for article in articles:
            url = str(article.url).strip().lower()
            if url in seen_urls:
                continue
            if any(self._similar_title(article.title, kept.title) for kept in unique):
                continue
            seen_urls.add(url)
            unique.append(article)
        return unique

    def _rank_articles(
        self, articles: list[Article], topics: list[str], custom_keywords: list[str]
    ) -> list[Article]:
        scored_articles = [self._score_article(article, topics, custom_keywords) for article in articles]
        return sorted(
            scored_articles,
            key=lambda article: (article.priority_score, self._published_timestamp(article.published_at)),
            reverse=True,
        )

    def _score_article(self, article: Article, topics: list[str], custom_keywords: list[str]) -> Article:
        keywords = [keyword.lower() for keyword in self._effective_keywords(topics, custom_keywords)]
        title = article.title.lower()
        description = (article.description or "").lower()
        title_keywords = [keyword for keyword in keywords if keyword in title]
        description_keywords = [
            keyword for keyword in keywords if keyword in description and keyword not in title
        ]
        title_matches = len(title_keywords)
        description_matches = len(description_keywords)
        recency_score = self._recency_score(article.published_at)
        detail_score = 4 if article.description else 0
        keyword_score = title_matches * 14 + description_matches * 6
        score = min(100, keyword_score + recency_score + detail_score)
        label = self._priority_label(score)
        reason_parts: list[str] = []
        matched_keywords = self._display_keywords(title_keywords + description_keywords)
        if matched_keywords:
            reason_parts.append(f"관심 키워드 일치: {', '.join(matched_keywords)}")
        else:
            reason_parts.append("직접 키워드 일치는 적지만 선택 언론사와 기간 조건에 포함")
        reason_parts.append(
            f"점수 구성: 제목 {title_matches}개 x14, 본문 {description_matches}개 x6, 최신성 +{recency_score}, 설명문 +{detail_score}"
        )
        reason_parts.append(f"최종 {score}점으로 상위 {label} 기사에 배치")
        if not reason_parts:
            reason_parts.append("선택 조건과의 기본 관련성")

        return article.model_copy(
            update={
                "priority_score": score,
                "priority_label": label,
                "priority_reason": ", ".join(reason_parts),
                "matched_keywords": matched_keywords,
            }
        )

    def _stats(
        self,
        *,
        request: BriefingRequest,
        fetch_report: FetchReport,
        matched_count: int,
        deduped_count: int,
        selected_count: int,
    ) -> BriefingStats:
        return BriefingStats(
            source_count=len(request.sources),
            collected_count=fetch_report.collected_count,
            matched_count=matched_count,
            deduped_count=deduped_count,
            selected_count=selected_count,
            attempted_feed_count=fetch_report.attempted_feed_count,
            failed_feed_count=fetch_report.failed_feed_count,
        )

    def _display_keywords(self, keywords: list[str], limit: int = 5) -> list[str]:
        unique: list[str] = []
        for keyword in keywords:
            normalized = keyword.strip()
            if not normalized or normalized in unique:
                continue
            unique.append(normalized.upper() if normalized in {"ai", "it", "llm"} else normalized)
            if len(unique) == limit:
                break
        return unique

    def _priority_label(self, score: int) -> str:
        if score >= 70:
            return "핵심"
        if score >= 50:
            return "높음"
        if score >= 30:
            return "보통"
        return "참고"

    def _recency_score(self, value: str | None) -> int:
        timestamp = self._published_timestamp(value)
        if timestamp == 0:
            return 0
        age_hours = max(0, (datetime.now(timezone.utc).timestamp() - timestamp) / 3600)
        if age_hours <= 12:
            return 26
        if age_hours <= 24:
            return 22
        if age_hours <= 72:
            return 14
        return 6

    def _published_timestamp(self, value: str | None) -> float:
        if not value:
            return 0
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return 0
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).timestamp()

    def _similar_title(self, left: str, right: str) -> bool:
        left_norm = self._normalize_title(left)
        right_norm = self._normalize_title(right)
        if not left_norm or not right_norm:
            return False
        return SequenceMatcher(None, left_norm, right_norm).ratio() >= 0.86

    def _normalize_title(self, value: str) -> str:
        return "".join(ch.lower() for ch in value if ch.isalnum())

    def _briefing_title(self, request: BriefingRequest) -> str:
        topics = ", ".join(self._focus_labels(request, self._custom_keywords(request)))
        period = "오늘" if request.date_range == "1d" else "최근 7일"
        return f"{period} {topics} 뉴스 브리핑"
