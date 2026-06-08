from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


EvidenceStrength = Literal["strong", "weak"]
RequirementSource = Literal["duckduckgo", "role_inference"]


class Agent2Request(BaseModel):
    target_role: str = Field(..., min_length=1, description="Target job role")
    company_type: str | None = Field(None, description="Preferred company type")
    max_results: int = Field(5, ge=1, le=10, description="Search result limit")


class JobPostingHit(BaseModel):
    title: str
    url: str
    snippet: str = ""
    source: str = "duckduckgo"
    fetched_text: str = ""
    fetch_ok: bool = False
    fetch_error: str | None = None


class CompanyEvidence(BaseModel):
    name: str
    url: str | None = None


class JobRequirement(BaseModel):
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    required_experience: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    companies: list[CompanyEvidence] = Field(default_factory=list)
    evidence_strength: EvidenceStrength = "weak"
    source: RequirementSource = "duckduckgo"
    source_urls: list[str] = Field(default_factory=list)
    postings: list[JobPostingHit] = Field(default_factory=list)
    summary: str = ""
    search_query: str = ""
    llm_used: bool = False
    degraded_reason: str | None = None


class JobRequirementOutput(BaseModel):
    companies: list[CompanyEvidence] = Field(default_factory=list, description="근거 기업")
    required_skills: list[str] = Field(default_factory=list, description="필수 기술")
    preferred_skills: list[str] = Field(default_factory=list, description="우대 기술")
    required_experience: list[str] = Field(default_factory=list, description="요구 경험")
    keywords: list[str] = Field(default_factory=list, description="핵심 키워드")


class HealthResponse(BaseModel):
    ok: bool
    service: str
