from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class Option(BaseModel):
    id: str
    label: str


class BriefingPreset(BaseModel):
    id: str
    label: str
    description: str
    sources: list[str]
    topics: list[str]
    custom_keywords: list[str] = Field(default_factory=list)
    exclude_keywords: list[str] = Field(default_factory=list)
    date_range: Literal["1d", "7d"]
    limit: int = Field(default=5, ge=1, le=10)


DemoScenario = BriefingPreset


class BriefingRequest(BaseModel):
    sources: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    custom_keywords: list[str] = Field(default_factory=list)
    exclude_keywords: list[str] = Field(default_factory=list)
    date_range: Literal["1d", "7d"] = "1d"
    limit: int = Field(default=5, ge=1, le=10)


class Article(BaseModel):
    title: str
    source: str
    url: HttpUrl | str
    published_at: str | None = None
    description: str | None = None
    topic: str | None = None
    summary: str | None = None
    why_it_matters: str | None = None
    priority_score: int = 0
    priority_label: str | None = None
    priority_reason: str | None = None
    matched_keywords: list[str] = Field(default_factory=list)


class BriefingStats(BaseModel):
    source_count: int = 0
    collected_count: int = 0
    matched_count: int = 0
    deduped_count: int = 0
    selected_count: int = 0
    attempted_feed_count: int = 0
    failed_feed_count: int = 0


class Briefing(BaseModel):
    title: str
    generated_at: datetime
    source_labels: list[str]
    topic_labels: list[str]
    custom_keywords: list[str] = Field(default_factory=list)
    exclude_keywords: list[str] = Field(default_factory=list)
    date_range: str
    common_topics: list[str]
    articles: list[Article]
    notices: list[str] = Field(default_factory=list)
    stats: BriefingStats = Field(default_factory=BriefingStats)
    used_sample_data: bool = False


class BriefingResponse(BaseModel):
    status: Literal["ok"]
    briefing: Briefing


class BriefingHistoryItem(BaseModel):
    id: int
    title: str
    created_at: str
    generated_at: datetime
    source_labels: list[str]
    topic_labels: list[str]
    custom_keywords: list[str] = Field(default_factory=list)
    exclude_keywords: list[str] = Field(default_factory=list)
    date_range: str
    article_count: int
    used_sample_data: bool = False


class FetchReport(BaseModel):
    source_count: int = 0
    collected_count: int = 0
    attempted_feed_count: int = 0
    failed_feed_count: int = 0


class SourceStatus(BaseModel):
    id: str
    label: str
    domain: str
    status: Literal["ok", "partial", "error"]
    feed_count: int
    ok_feed_count: int
    article_count: int
    checked_at: datetime
    message: str


class BriefingProfileInput(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    sources: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    custom_keywords: list[str] = Field(default_factory=list)
    exclude_keywords: list[str] = Field(default_factory=list)
    date_range: Literal["1d", "7d"] = "1d"
    limit: int = Field(default=5, ge=1, le=10)


class BriefingProfile(BriefingProfileInput):
    id: int
    created_at: str
