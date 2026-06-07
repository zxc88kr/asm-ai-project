from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from backend.app.catalog import SOURCES, SOURCE_BY_ID, SourceOption, source_labels, topic_keywords
from backend.app.models import Article, FetchReport, SourceStatus
from backend.app.sample_data import SAMPLE_ARTICLES


NEWS_API_URL = "https://newsapi.org/v2/everything"
USER_AGENT = "ASM4-NewsCurator/1.0 (+rss briefing agent)"


class NewsClient:
    def __init__(self, api_key: str | None, *, use_rss: bool = True) -> None:
        self.api_key = api_key
        self.use_rss = use_rss

    def fetch(
        self,
        *,
        sources: list[str],
        topics: list[str],
        custom_keywords: list[str] | None = None,
        date_range: str,
        limit: int,
    ) -> tuple[list[Article], list[str], bool, FetchReport]:
        if self.use_rss:
            rss_articles, rss_notices, rss_report = self._fetch_rss(
                sources=sources,
                date_range=date_range,
                limit=limit,
            )
            if rss_articles:
                return rss_articles, rss_notices, False, rss_report

        if self.api_key:
            return self._fetch_news_api(
                sources=sources,
                topics=topics,
                custom_keywords=custom_keywords or [],
                date_range=date_range,
                limit=limit,
            )

        sample = self._sample_articles(sources=sources, topics=topics, limit=limit)
        notices = ["RSS에서 관련 뉴스를 가져오지 못해 샘플 뉴스로 브리핑을 생성했습니다."]
        report = FetchReport(source_count=len(sources), collected_count=len(sample))
        return sample, notices, True, report

    def _fetch_rss(
        self,
        *,
        sources: list[str],
        date_range: str,
        limit: int,
    ) -> tuple[list[Article], list[str], FetchReport]:
        selected_sources = [SOURCE_BY_ID[source_id] for source_id in sources if source_id in SOURCE_BY_ID]
        unsupported = [source.label for source in selected_sources if not source.rss_urls]
        articles: list[Article] = []
        failed_feeds: list[str] = []
        attempted_feed_count = 0

        for source in selected_sources:
            for feed_url in source.rss_urls:
                attempted_feed_count += 1
                try:
                    articles.extend(self._read_feed(source, feed_url))
                except Exception:
                    failed_feeds.append(source.label)

        articles = self._filter_by_date(articles, date_range)
        articles = self._dedupe_by_url(articles)
        articles = sorted(articles, key=lambda article: self._published_timestamp(article.published_at), reverse=True)

        notices: list[str] = []
        if articles:
            notices.append(f"RSS 피드에서 실제 뉴스 {min(len(articles), limit)}건을 수집했습니다.")
        if unsupported:
            notices.append(f"공개 RSS를 찾지 못한 언론사는 제외했습니다: {', '.join(sorted(set(unsupported)))}")
        if failed_feeds:
            notices.append(f"일부 RSS 피드를 읽지 못했습니다: {', '.join(sorted(set(failed_feeds)))}")

        report = FetchReport(
            source_count=len(selected_sources),
            collected_count=len(articles),
            attempted_feed_count=attempted_feed_count,
            failed_feed_count=len(failed_feeds),
        )
        return articles[: max(limit * 4, 20)], notices, report

    def source_statuses(self) -> list[SourceStatus]:
        checked_at = datetime.now(timezone.utc)
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(self._source_status, source, checked_at): source.id
                for source in SOURCES
            }
            results: dict[str, SourceStatus] = {}
            for future in as_completed(futures):
                results[futures[future]] = future.result()
        return [results[source.id] for source in SOURCES]

    def _source_status(self, source: SourceOption, checked_at: datetime) -> SourceStatus:
        ok_feed_count = 0
        article_count = 0
        errors: list[str] = []
        for feed_url in source.rss_urls:
            try:
                feed_articles = self._read_feed(source, feed_url)
            except Exception as exc:
                errors.append(f"{feed_url}: {type(exc).__name__}")
                continue
            ok_feed_count += 1
            article_count += len(feed_articles)

        if ok_feed_count == len(source.rss_urls):
            status = "ok"
            message = f"RSS {ok_feed_count}개 정상, 기사 {article_count}건 확인"
        elif ok_feed_count > 0:
            status = "partial"
            message = f"RSS {ok_feed_count}/{len(source.rss_urls)}개 정상, 기사 {article_count}건 확인"
        else:
            status = "error"
            message = errors[0] if errors else "확인 가능한 RSS 피드가 없습니다."

        return SourceStatus(
            id=source.id,
            label=source.label,
            domain=source.domain,
            status=status,
            feed_count=len(source.rss_urls),
            ok_feed_count=ok_feed_count,
            article_count=article_count,
            checked_at=checked_at,
            message=message,
        )

    def _read_feed(self, source: SourceOption, feed_url: str) -> list[Article]:
        request = Request(feed_url, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=10) as response:
            payload = response.read(2_000_000)
        root = ET.fromstring(payload)

        items = list(root.findall(".//item"))
        if not items:
            items = list(root.findall(".//{*}entry"))

        articles: list[Article] = []
        for item in items:
            title = self._text(item, ("title",))
            link = self._rss_link(item)
            description = self._clean_html(
                self._text(item, ("description", "summary", "content", "{http://purl.org/rss/1.0/modules/content/}encoded"))
            )
            published_at = self._normalize_date(
                self._text(item, ("pubDate", "published", "updated", "{http://purl.org/dc/elements/1.1/}date"))
            )
            if title and link:
                articles.append(
                    Article(
                        title=self._clean_html(title),
                        source=source.label,
                        url=link,
                        published_at=published_at,
                        description=description or None,
                    )
                )
        return articles

    def _rss_link(self, item: ET.Element) -> str:
        link = self._text(item, ("link",))
        if link:
            return link
        for child in item:
            if child.tag.endswith("link"):
                href = child.attrib.get("href")
                if href:
                    return href.strip()
        return ""

    def _text(self, item: ET.Element, names: tuple[str, ...]) -> str:
        for name in names:
            child = item.find(name)
            if child is None:
                child = item.find(f".//{{*}}{name}")
            if child is not None and child.text:
                return child.text.strip()
        return ""

    def _clean_html(self, value: str) -> str:
        text = re.sub(r"<[^>]+>", " ", value or "")
        text = unescape(text)
        return re.sub(r"\s+", " ", text).strip()

    def _normalize_date(self, value: str) -> str | None:
        if not value:
            return None
        try:
            parsed = parsedate_to_datetime(value)
        except (TypeError, ValueError, IndexError):
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).isoformat()

    def _filter_by_date(self, articles: list[Article], date_range: str) -> list[Article]:
        days = 1 if date_range == "1d" else 7
        threshold = datetime.now(timezone.utc) - timedelta(days=days)
        filtered = [
            article
            for article in articles
            if self._published_timestamp(article.published_at) == 0
            or datetime.fromtimestamp(self._published_timestamp(article.published_at), tz=timezone.utc) >= threshold
        ]
        return filtered or articles

    def _dedupe_by_url(self, articles: list[Article]) -> list[Article]:
        unique: list[Article] = []
        seen_urls: set[str] = set()
        for article in articles:
            url = str(article.url).strip().lower()
            if url in seen_urls:
                continue
            seen_urls.add(url)
            unique.append(article)
        return unique

    def _fetch_news_api(
        self,
        *,
        sources: list[str],
        topics: list[str],
        custom_keywords: list[str],
        date_range: str,
        limit: int,
    ) -> tuple[list[Article], list[str], bool, FetchReport]:
        query_keywords = topic_keywords(topics) + custom_keywords
        query = " OR ".join(list(dict.fromkeys(query_keywords))) or "뉴스"
        domains = ",".join(
            source.domain for source_id in sources if (source := SOURCE_BY_ID.get(source_id))
        )
        days = 1 if date_range == "1d" else 7
        from_date = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
        params = {
            "q": query,
            "from": from_date,
            "sortBy": "publishedAt",
            "language": "ko",
            "pageSize": min(max(limit * 4, 10), 50),
            "apiKey": self.api_key,
        }
        if domains:
            params["domains"] = domains

        url = f"{NEWS_API_URL}?{urlencode(params)}"
        request = Request(url, headers={"User-Agent": USER_AGENT})

        try:
            with urlopen(request, timeout=12) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            sample = self._sample_articles(sources=sources, topics=topics, limit=limit)
            report = FetchReport(source_count=len(sources), collected_count=len(sample))
            return sample, [f"뉴스 API 오류로 샘플 뉴스로 전환했습니다: {exc}"], True, report

        if payload.get("status") != "ok":
            message = payload.get("message", "뉴스 API 응답이 정상 상태가 아닙니다.")
            sample = self._sample_articles(sources=sources, topics=topics, limit=limit)
            report = FetchReport(source_count=len(sources), collected_count=len(sample))
            return sample, [f"{message} 샘플 뉴스로 전환했습니다."], True, report

        articles = [self._to_article(item) for item in payload.get("articles", [])]
        articles = [article for article in articles if article.title and article.url]
        if not articles:
            sample = self._sample_articles(sources=sources, topics=topics, limit=limit)
            report = FetchReport(source_count=len(sources), collected_count=len(sample))
            return sample, ["관련 뉴스가 없어 샘플 뉴스로 브리핑을 생성했습니다."], True, report

        report = FetchReport(source_count=len(sources), collected_count=len(articles))
        return articles, ["NewsAPI에서 실제 뉴스를 수집했습니다."], False, report

    def _to_article(self, item: dict[str, Any]) -> Article:
        source = item.get("source") or {}
        return Article(
            title=(item.get("title") or "").strip(),
            source=(source.get("name") or "알 수 없음").strip(),
            url=item.get("url") or "",
            published_at=item.get("publishedAt"),
            description=(item.get("description") or item.get("content") or "").strip() or None,
        )

    def _sample_articles(self, *, sources: list[str], topics: list[str], limit: int) -> list[Article]:
        selected_source_labels = set(source_labels(sources))
        selected_topics = set(topics)
        articles = [
            article
            for article in SAMPLE_ARTICLES
            if (not selected_source_labels or article.source in selected_source_labels)
            and (not selected_topics or article.topic in selected_topics)
        ]
        if not articles:
            articles = SAMPLE_ARTICLES
        return articles[: max(limit * 4, 20)]

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
