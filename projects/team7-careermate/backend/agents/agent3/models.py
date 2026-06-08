"""Agent3 Pydantic models.

CareerMate Agent3(gap_analysis + roadmap_plan + roadmap_critic)가 주고받는
모든 데이터 구조를 정의한다. 설계 근거는 docs/06-data-model.md.

모델 분류:
  - 입력(소비): ProfileDiagnosis(에이전트1), JobRequirement(에이전트2), EpisodicMemory
  - 툴 반환: SearchHit(web_search), SkillRecord(lookup_skill), ResourceItem
  - Agent3 출력: GapAnalysis, Roadmap, CriticReport
  - 횡단: TraceEntry
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ─────────────────────────────────────────────────────────────
# Enum 정의 (docs/06-data-model.md §3)
# ─────────────────────────────────────────────────────────────
class SkillStatus(str, Enum):
    known = "known"        # 스킬 DB 존재 → verified=True
    unknown = "unknown"    # 미존재 → web_search/LLM 폴백 + verified=False


class CriticVerdict(str, Enum):
    pass_ = "pass"         # 4종 체크리스트 전부 통과 → finalize
    revise = "revise"      # 위반 존재 → roadmap_plan 루프백


class ViolationType(str, Enum):
    uncovered_gap = "uncovered_gap"
    time_budget_exceeded = "time_budget_exceeded"
    prereq_order_violation = "prereq_order_violation"
    forbidden_phrase = "forbidden_phrase"


class EvidenceStrength(str, Enum):
    strong = "strong"
    weak = "weak"


class MemoryStatus(str, Enum):
    new_user = "new_user"
    returning_user = "returning_user"


class RoadmapHorizon(str, Enum):
    weeks_4 = "weeks_4"
    weeks_6 = "weeks_6"
    weeks_8 = "weeks_8"


class SourceOrigin(str, Enum):
    db = "db"      # 스킬DB 검수 url (최고 신뢰)
    web = "web"    # web_search 결과 url ("웹 출처" 뱃지)
    llm = "llm"    # LLM 순수 자체지식 (url 없음, "검증 안 됨" 뱃지)


class PriorityLevel(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


# ─────────────────────────────────────────────────────────────
# 툴 반환 모델 — web_search / lookup_skill
# ─────────────────────────────────────────────────────────────
class SearchHit(BaseModel):
    """web_search() 반환 단건. snippet은 검색 API 발췌(크롤링 아님)."""

    title: str
    url: str                       # 출처 URL (verified=true 근거)
    snippet: str = ""
    source: str = ""               # 도메인 또는 제공자명 (예: "tavily")
    retrieved_at: str = ""         # ISO 타임스탬프 (검색 시각)


class ResourceItem(BaseModel):
    """학습 자원 단건. origin으로 출처 3단계(db/web/llm)를 구분한다."""

    title: str
    url: Optional[str] = None              # db/web 유래; llm 폴백은 None
    type: str = "doc"                      # "course" | "doc" | "project"
    verified: bool = False                 # url 출처 있으면 True (db 또는 web)
    origin: SourceOrigin = SourceOrigin.db
    source_url: Optional[str] = None       # web origin일 때 SearchHit.url


class SkillRecord(BaseModel):
    """lookup_skill() 반환. 미존재 시 status=unknown 폴백(예외 throw 금지)."""

    name: str
    status: SkillStatus
    prereqs: list[str] = Field(default_factory=list)
    resources: list[ResourceItem] = Field(default_factory=list)
    typical_hours: int = 0
    verified: bool = False


# ─────────────────────────────────────────────────────────────
# 입력 모델 — 에이전트 1 (profile_diagnosis)
# ─────────────────────────────────────────────────────────────
class ProfileDiagnosis(BaseModel):
    """에이전트1(profile_diagnosis) 출력. feature/Agent_2의 ProfileDiagnosis와 동일 스키마.

    온보딩 8필드를 그대로 보존(major~concern)하고 LLM 정성 진단을 덧붙인다.
    주의: strengths/weaknesses는 스킬명이 아니라 정성 개념("개발 경험 부족", "전공 일치도")이다.
    실제 보유 스킬은 **owned_skills**이며, 갭 분석의 "보유" 기준은 이것을 쓴다.
    weekly_hours·target_role도 이 안에서 직접 읽는다.
    """

    model_config = ConfigDict(extra="ignore")

    # ── 온보딩 원본 보존 (에이전트1이 입력값 그대로 복사) ──
    major: str = ""
    current_status: str = ""
    interests: list[str] = Field(default_factory=list)
    owned_skills: list[str] = Field(default_factory=list)       # 실제 보유 스킬(갭 "보유" 기준)
    target_role: str = ""
    company_type: Optional[str] = None
    weekly_hours: int = 0
    concern: list[str] = Field(default_factory=list)

    # ── LLM 정성 진단 ──
    summary: str = ""
    strengths: list[str] = Field(default_factory=list)          # 정성 개념(스킬명 아님)
    weaknesses: list[str] = Field(default_factory=list)         # 정성 개념(스킬명 아님)
    evidence: dict[str, str] = Field(default_factory=dict)


# ─────────────────────────────────────────────────────────────
# 입력 모델 — 에이전트 2 (job_requirement)
# ─────────────────────────────────────────────────────────────
class JobRequirement(BaseModel):
    """에이전트2 출력.

    feat/agent2의 실제 JobRequirement는 docs 스펙보다 필드가 많고(companies,
    source_urls, postings, summary 등) source 값도 "duckduckgo"를 쓴다.
    Agent3는 핵심 필드만 사용하고 나머지는 무시(extra="ignore")해 그대로 파싱한다.
    """

    model_config = ConfigDict(extra="ignore")

    required_skills: list[str] = Field(default_factory=list)    # 자연어 문장일 수 있음
    preferred_skills: list[str] = Field(default_factory=list)
    required_experience: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)           # 스킬명 추출 힌트
    # 에이전트2가 주지 않을 수 있는 값. None이면 Agent3가 데이터 충실도로 추론한다.
    evidence_strength: Optional[EvidenceStrength] = None
    source: str = "role_inference"


# ─────────────────────────────────────────────────────────────
# Agent3 출력 — gap_analysis
# ─────────────────────────────────────────────────────────────
class GapItem(BaseModel):
    skill: str                              # 정규화된 부족 스킬명 (normalize_skill_name 후)
    priority: PriorityLevel = PriorityLevel.medium
    current_level: str = "없음"             # 사용자 현재 수준
    target_level: str = "실무"              # 목표 요구 수준
    skill_status: SkillStatus = SkillStatus.unknown   # lookup_skill 결과
    verified: bool = False                  # known=True, unknown=False


class GapAnalysis(BaseModel):
    gaps: list[GapItem] = Field(default_factory=list)   # 우선순위 정렬
    job_evidence_strength: EvidenceStrength = EvidenceStrength.weak
    needs_rerun: bool = False                           # True → job_requirement 재요청
    rerun_reason: Optional[str] = None


# ─────────────────────────────────────────────────────────────
# Agent3 출력 — roadmap_plan
# ─────────────────────────────────────────────────────────────
class TaskItem(BaseModel):
    title: str
    skill: str                                          # 연결 부족 스킬
    resources: list[ResourceItem] = Field(default_factory=list)
    est_hours: int = 0
    verified: bool = False


class WeekPlan(BaseModel):
    week_index: int                                     # 주차 (1-base)
    objectives: list[str] = Field(default_factory=list)
    tasks: list[TaskItem] = Field(default_factory=list)
    covered_skills: list[str] = Field(default_factory=list)
    planned_hours: int = 0                              # ≤ weekly_hours_budget 검증 대상
    phase: Optional[str] = None                         # 소속 단계명(LLM 부여). phases 묶음 기준


# ── UI 카드(단계) 뷰 — phases는 weeks를 묶어 보여주기 위한 파생 구조 ──
class ChecklistItem(BaseModel):
    """대시보드 단계 카드의 체크리스트 항목 1개.

    completed/진행률은 Agent3가 넣지 않는다(사용자 런타임 상태 → 백엔드 소유).
    id는 백엔드가 완료 상태를 매핑하는 안정 키다.
    """

    id: str                                             # 안정 식별자 (예: "p1-i2")
    label: str                                          # 표시 라벨 (예: "개발 환경 세팅")
    skill: str = ""                                     # 연결 스킬 (활동성 항목은 "")
    resources: list[ResourceItem] = Field(default_factory=list)
    est_hours: int = 0


class Phase(BaseModel):
    """UI 로드맵 카드 1개 = 연속된 주차 묶음."""

    index: int                                          # 1-base 단계 번호
    title: str                                          # 단계명 (예: "기초 다지기")
    week_from: int
    week_to: int
    items: list[ChecklistItem] = Field(default_factory=list)


class Roadmap(BaseModel):
    horizon: RoadmapHorizon = RoadmapHorizon.weeks_8
    total_weeks: int = 0
    weeks: list[WeekPlan] = Field(default_factory=list)     # 주차 상세 (검증·계산용)
    phases: list[Phase] = Field(default_factory=list)       # 단계 카드 (UI 렌더용, weeks 파생)
    weekly_hours_budget: int = 0                        # 사용자 가용 시간(검증 기준 복사)
    rationale: str = ""                                 # 기간 산출 근거 (Plan-and-Solve)


# ─────────────────────────────────────────────────────────────
# 입력 모델 — episodic memory
# ─────────────────────────────────────────────────────────────
class WeeklyProgress(BaseModel):
    week_index: int                                     # 주차 (1-base)
    completed: bool = False                             # 대시보드 체크박스
    note: Optional[str] = None


class EpisodicMemory(BaseModel):
    status: MemoryStatus = MemoryStatus.new_user
    last_roadmap: Optional[Roadmap] = None              # 직전 로드맵 (없으면 None)
    weekly_progress: list[WeeklyProgress] = Field(default_factory=list)
    last_updated: str = ""                              # ISO 타임스탬프


# ─────────────────────────────────────────────────────────────
# Agent3 출력 — roadmap_critic
# ─────────────────────────────────────────────────────────────
class Violation(BaseModel):
    type: ViolationType
    detail: str                                         # 위반 상세
    location: str                                       # 위반 위치 (예: "week 3")


class CriticReport(BaseModel):
    verdict: CriticVerdict = CriticVerdict.pass_
    violations: list[Violation] = Field(default_factory=list)   # pass면 빈 리스트
    checked_at_revision: int = 0                                # 검증 시점 revision_count


# ─────────────────────────────────────────────────────────────
# 횡단 — 실행 트레이스
# ─────────────────────────────────────────────────────────────
class TraceEntry(BaseModel):
    node: str
    input_summary: str = ""
    decision: Optional[str] = None                      # 분기 결정 (라우터·critic·되먹임만)
    tool_called: Optional[str] = None                   # 예: "lookup_skill"
    output_summary: str = ""
    ts: str = ""                                        # ISO 타임스탬프


# ─────────────────────────────────────────────────────────────
# 최종 출력 — 사용자 전달 산출물 (docs/06-data-model.md §2-12)
# ─────────────────────────────────────────────────────────────
class FinalOutput(BaseModel):
    profile: ProfileDiagnosis
    gap_analysis: GapAnalysis
    roadmap: Roadmap
    verified: bool = True
    trace_summary: list[TraceEntry] = Field(default_factory=list)
    disclaimer: str = ""
    search_degraded: bool = False
