from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from backend.app.models import Article


class Summarizer:
    def __init__(self, *, api_key: str | None, model: str, base_url: str) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    def summarize(
        self, articles: list[Article], topic_labels: list[str]
    ) -> tuple[list[Article], list[str], list[str]]:
        if not articles:
            return [], [], []
        if not self.api_key:
            return self._fallback(articles, topic_labels), self._common_topics(articles, topic_labels), [
                "UPSTAGE_API_KEY가 없어 로컬 요약을 사용했습니다."
            ]

        try:
            payload = self._call_upstage(articles, topic_labels)
            return self._merge_ai_result(articles, payload), payload.get("common_topics", []), []
        except Exception as exc:
            summarized = self._fallback(articles, topic_labels)
            common_topics = self._common_topics(articles, topic_labels)
            notices = [f"Upstage 요약 API 오류로 로컬 요약을 사용했습니다: {exc}"]
            return summarized, common_topics, notices

    def _call_upstage(self, articles: list[Article], topic_labels: list[str]) -> dict[str, Any]:
        article_payload = [
            {
                "index": index,
                "title": article.title,
                "source": article.source,
                "published_at": article.published_at,
                "description": article.description,
            }
            for index, article in enumerate(articles)
        ]
        body = {
            "model": self.model,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "당신은 객관적이고 중립적인 뉴스 브리핑 에이전트입니다. "
                        "원문에 없는 사실, 정치적 의견, 투자 추천, 진위 판단을 추가하지 마세요. "
                        "반드시 설명 없이 유효한 JSON 객체만 출력하세요."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "topics": topic_labels,
                            "instructions": {
                                "article_summary": "기사별 요약은 한국어 2문장 이내",
                                "why_it_matters": "사용자가 왜 봐야 하는지 중립적으로 1문장",
                                "common_topics": "기사 전반의 공통 핵심 이슈 1~3개",
                            },
                            "articles": article_payload,
                            "output_schema": {
                                "common_topics": ["공통 핵심 이슈"],
                                "articles": [
                                    {
                                        "index": 0,
                                        "summary": "요약",
                                        "why_it_matters": "중요한 이유",
                                    }
                                ],
                            },
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
        }
        request = Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=30) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc

        content = response_payload["choices"][0]["message"]["content"]
        return self._parse_json_content(content)

    def _parse_json_content(self, content: str) -> dict[str, Any]:
        text = content.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return json.loads(text)

    def _merge_ai_result(self, articles: list[Article], payload: dict[str, Any]) -> list[Article]:
        by_index = {
            int(item["index"]): item
            for item in payload.get("articles", [])
            if isinstance(item, dict) and "index" in item
        }
        merged: list[Article] = []
        for index, article in enumerate(articles):
            summary = by_index.get(index, {})
            merged.append(
                article.model_copy(
                    update={
                        "summary": summary.get("summary") or article.description or article.title,
                        "why_it_matters": summary.get("why_it_matters")
                        or "선택한 관심 분야와 관련된 최신 흐름을 파악하는 데 도움이 됩니다.",
                    }
                )
            )
        return merged

    def _fallback(self, articles: list[Article], topic_labels: list[str]) -> list[Article]:
        topic_text = ", ".join(topic_labels) if topic_labels else "선택한 관심 분야"
        summarized: list[Article] = []
        for article in articles:
            description = article.description or article.title
            summary = description
            if len(summary) > 160:
                summary = summary[:157].rstrip() + "..."
            summarized.append(
                article.model_copy(
                    update={
                        "summary": summary,
                        "why_it_matters": f"{topic_text} 흐름을 빠르게 확인할 수 있는 기사입니다.",
                    }
                )
            )
        return summarized

    def _common_topics(self, articles: list[Article], topic_labels: list[str]) -> list[str]:
        if topic_labels:
            return [f"{label} 관련 주요 이슈가 이어지고 있습니다." for label in topic_labels[:3]]
        sources = sorted({article.source for article in articles})
        return [f"{', '.join(sources[:3])} 등에서 다룬 주요 이슈입니다."]
