# 에이전트 그래프 (노드·엣지·State) ★핵심

이 문서는 CareerMate의 LangGraph 에이전트 그래프 전체 구조를 정의합니다. State 스키마, 노드 역할, conditional edge 조건(의사코드), 전체 흐름 ASCII 다이어그램, 그리고 `graph.add_node` / `add_conditional_edges` 스케치를 포함합니다. 학생이 이 문서를 보고 바로 구현 코드로 옮길 수 있는 계약(contract) 수준으로 작성되었습니다.

> **LangGraph 한 줄 소개**: 에이전트의 실행 흐름을 "노드(node) = 처리 단계"와 "엣지(edge) = 다음 단계로의 연결"로 구성된 방향 그래프로 표현하는 프레임워크입니다. 특히 **conditional edge**를 사용하면 상태(State)의 값에 따라 다음 노드를 동적으로 선택할 수 있어, 자율 라우팅·루프·되먹임을 자연스럽게 표현합니다([LangGraph 공식 문서 — Conditional Edges](https://langchain-ai.github.io/langgraph/)).

---

## 1. 전체 그래프 ASCII 다이어그램

아래 그림은 그래프의 모든 분기·루프백·되먹임 화살표를 포함합니다.

```
START
  │
  ▼
┌──────────────────────┐
│  onboarding_intake   │  ← 프론트 입력 구조화, episodic_memory 조회
└──────────────────────┘
  │
  ▼
┌──────────────────────────┐
│  progress_reconciliation │  ← returning_user면 이월·진척 컨텍스트 주입
└──────────────────────────┘
  │
  ▼
┌──────────────────────┐
│    triage_router     │  ← ambiguity_score 산정 (0.0 ~ 1.0)
└──────────────────────┘
  │              │
  │ proceed      │ ask
  ▼              ▼
┌──────────┐  ┌─────────┐
│ profile_ │  │ clarify │  ← 2~3개 역질문 or 유사직무 제안
│diagnosis │  └─────────┘
└──────────┘       │
  │                │ (clarify_answers 수집 후 재산정)
  │                └──────────────────────┐
  │                                       │ (triage_router로 복귀)
  ▼                                ◄──────┘
  │
  ▼
┌──────────────────────┐
│   job_requirement    │  ← 직무 요구역량 추출, evidence_strength 표기
└──────────────────────┘
  │
  ▼
┌──────────────────────┐
│    gap_analysis      │  ← 부족역량 도출, needs_rerun 판단
└──────────────────────┘
  │                    │
  │ needs_rerun=false  │ needs_rerun=true
  │ or rerun_count≥1   │ AND rerun_count<1
  │                    ▼
  │             ┌──────────────────────┐
  │             │   job_requirement    │  ← rerun_reason 반영 재추출
  │             │   (재실행, 1회 한정) │
  │             └──────────────────────┘
  │                    │
  │◄───────────────────┘
  ▼
┌──────────────────────┐
│    roadmap_plan      │  ← lookup_skill 호출, 동적 기간 로드맵 생성
└──────────────────────┘
  │             ▲
  ▼             │ revise (위반 사유 전달)
┌──────────────────────┐
│   roadmap_critic     │  ← 4종 체크리스트 검증
└──────────────────────┘
  │              │
  │ pass         │ revise AND revision_count<2
  │ or count≥2   └──────────────────────────────┘
  ▼
┌──────────────────────┐
│      finalize        │  ← final_output 조립, trace 요약 첨부
└──────────────────────┘
  │
  ▼
 END
```

> **핵심 루프 3개 요약**
> - **Triage 루프**: `triage_router` → `clarify` → `triage_router` (clarify 후 재산정, 통상 proceed로 수렴)
> - **Gap→Job 되먹임**: `gap_analysis` → `job_requirement` (최대 1회, `rerun_count` 가드)
> - **Critic 루프**: `roadmap_critic` → `roadmap_plan` (최대 2회, `revision_count` 가드)

---

## 2. LangGraph State 스키마

State는 그래프 전체가 공유하는 단일 딕셔너리입니다. 각 노드는 필요한 키만 읽고, 담당 키만 씁니다.

| 키 | 타입 | 쓰는 노드 | 설명 |
|---|---|---|---|
| `user_id` | `str` | onboarding_intake | 사용자 식별자. episodic 메모리 조회/저장 키. |
| `session_id` | `str` | onboarding_intake | 이번 실행 세션 식별자. trace 로그 그룹핑용. |
| `onboarding_input` | `OnboardingInput` | onboarding_intake | 온보딩 원본 입력(전공/현재상태/관심분야/보유기술/목표직무/희망기업유형/주당가용시간/현재고민/공고텍스트). |
| `clarify_answers` | `list[ClarifyAnswer]` | clarify | 역질문 응답 수집. ask 경로에서만 채워짐. proceed면 빈 리스트. |
| `ambiguity_score` | `float` | triage_router | 0.0~1.0 모호도. `AMBIGUITY_THRESHOLD` 초과 시 ask 분기. |
| `route_decision` | `RouteDecision` | triage_router | ask \| proceed. conditional_edge 조건값. |
| `profile` | `ProfileDiagnosis` | profile_diagnosis | 현재역량 요약/강점/약점/관심분야/준비수준. |
| `job_requirement` | `JobRequirement` | job_requirement | 필수기술/우대기술/요구경험/핵심키워드/근거신뢰도. |
| `gap_analysis` | `GapAnalysis` | gap_analysis | 부족역량 리스트+우선순위+job 근거강도 평가. |
| `roadmap` | `Roadmap` | roadmap_plan | 주차별 학습목표·실습과제·시간. 동적 task decomposition 결과. |
| `critic_report` | `CriticReport` | roadmap_critic | 검증 결과(verdict + 위반 항목 리스트). |
| `needs_rerun` | `bool` | gap_analysis | job 근거 약하면 true. job_requirement 재요청 트리거. |
| `rerun_reason` | `str \| None` | gap_analysis | needs_rerun=true일 때 재요청 사유. job_requirement 재실행 컨텍스트. |
| `rerun_count` | `int` | gap_analysis, job_requirement | Gap→Job 되먹임 실행 횟수. MAX_RERUN(=1) 도달 시 재요청 중단. |
| `revision_count` | `int` | roadmap_critic | Critic→Plan 재생성 횟수. MAX_REVISIONS(=2) 도달 시 강제 finalize. |
| `episodic_memory` | `EpisodicMemory \| None` | onboarding_intake | 재방문 사용자의 직전 로드맵+주차 진행기록. 신규 사용자면 None. |
| `trace` | `list[TraceEntry]` | 모든 노드 (append) | 노드별 실행 로그. append-only. 대시보드 'why-this-path' 타임라인용. |
| `verified` | `bool` | gap_analysis, roadmap_critic | 전역 검증 플래그. lookup_skill 폴백 항목 혼입 시 false로 강등. |
| `final_output` | `FinalOutput \| None` | finalize | 사용자 전달용 최종 산출물. 종료 전까지 None. |
| `error` | `str \| None` | 모든 노드 (예외 시) | 복구 불가 오류. MVP: finalize가 error 존재 시 부분결과+오류안내 출력(단축 엣지는 향후 확장). |
| `search_results` | `dict[str, list[SearchHit]]` | `job_requirement`, `roadmap_plan`, `gap_analysis` | query→SearchHit 리스트 세션 캐시(동일 쿼리 재호출 방지). append/merge. |
| `search_count` | `int` | 검색 호출 노드 전부 | 세션 누적 web_search 실제 API 호출 횟수. `MAX_SEARCH` 가드. 노드 본문에서 += 1. |
| `search_degraded` | `bool` | 검색 호출 노드 전부 | 검색 실패 또는 `MAX_SEARCH` 초과 1회라도 발생 시 True. finalize disclaimer에 반영. |

### TypedDict 스케치 (Python)

```python
from typing import TypedDict, Optional
from pydantic import BaseModel

class AgentState(TypedDict):
    user_id: str
    session_id: str
    onboarding_input: OnboardingInput
    clarify_answers: list[ClarifyAnswer]
    ambiguity_score: float
    route_decision: str          # "ask" | "proceed"
    profile: Optional[ProfileDiagnosis]
    job_requirement: Optional[JobRequirement]
    gap_analysis: Optional[GapAnalysis]
    roadmap: Optional[Roadmap]
    critic_report: Optional[CriticReport]
    needs_rerun: bool
    rerun_reason: Optional[str]
    rerun_count: int             # MAX_RERUN = 1
    revision_count: int          # MAX_REVISIONS = 2
    episodic_memory: Optional[EpisodicMemory]
    trace: list[TraceEntry]      # append-only
    verified: bool
    final_output: Optional[FinalOutput]
    error: Optional[str]
    search_results: dict          # dict[str, list[SearchHit]] — query→결과 세션 캐시
    search_count: int             # MAX_SEARCH = 8, 노드 본문에서 += 1
    search_degraded: bool         # 검색 실패/상한 초과 시 True
```

---

## 3. Pydantic 모델 스케치

> Pydantic은 Python의 데이터 검증 라이브러리입니다. `BaseModel`을 상속하면 필드 타입 체크와 JSON 직렬화를 자동으로 해줍니다.

```python
from pydantic import BaseModel
from typing import Optional
from enum import Enum

# ── Enum 정의 ──────────────────────────────────────────────
class RouteDecision(str, Enum):
    ask = "ask"
    proceed = "proceed"

class SkillStatus(str, Enum):
    known = "known"
    unknown = "unknown"

class CriticVerdict(str, Enum):
    pass_ = "pass"
    revise = "revise"

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

class PriorityLevel(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"

class RoadmapHorizon(str, Enum):
    weeks_4 = "weeks_4"
    weeks_6 = "weeks_6"
    weeks_8 = "weeks_8"

# ── 온보딩 입력 ────────────────────────────────────────────
class OnboardingInput(BaseModel):
    major: str                         # 전공/직무 배경
    current_status: str                # 재학/취준 등
    interests: list[str]               # 관심 분야
    owned_skills: list[str]            # 보유 기술(자유표기)
    target_role: str                   # 목표 직무(IT 한정)
    company_type: Optional[str]        # 희망 기업 유형
    weekly_hours: int                  # 주당 가용 시간
    concern: Optional[str]             # 현재 고민
    job_posting_text: Optional[str]    # 공고 텍스트(없으면 샘플)

class ClarifyAnswer(BaseModel):
    question: str                      # 에이전트가 던진 역질문
    answer: str                        # 사용자 응답
    kind: str                          # "info_supplement" | "similar_role_pick"

# ── 에이전트 출력 ──────────────────────────────────────────
class ProfileDiagnosis(BaseModel):
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    interests: list[str]
    readiness_level: str               # "low" | "mid" | "high"
    evidence: dict[str, str]           # 강점/약점 → 근거 원문 (예: {"React 경험": "이력서 3번 항목"})

class JobRequirement(BaseModel):
    required_skills: list[str]
    preferred_skills: list[str]
    required_experience: list[str]
    keywords: list[str]
    evidence_strength: EvidenceStrength
    source: str                        # "user_posting" | "sample_posting" | "role_inference" | "web_search"

class GapItem(BaseModel):
    skill: str
    priority: PriorityLevel
    current_level: str
    target_level: str
    skill_status: SkillStatus
    verified: bool

class GapAnalysis(BaseModel):
    gaps: list[GapItem]
    job_evidence_strength: EvidenceStrength
    needs_rerun: bool
    rerun_reason: Optional[str]

# ── 웹검색 결과 ────────────────────────────────────────────
class SearchHit(BaseModel):
    title: str            # 검색 결과 제목
    url: str              # 출처 URL (verified=true 근거)
    snippet: str          # 검색 API가 반환한 본문 발췌(크롤링 아님)
    source: str           # 도메인 또는 제공자명 (예: "wanted.co.kr", "tavily")
    retrieved_at: str     # ISO 타임스탬프 (검색 시각)

# ── 로드맵 ─────────────────────────────────────────────────
class ResourceItem(BaseModel):
    title: str
    url: Optional[str]                 # 사전 유래만; 폴백은 None
    type: str                          # "course" | "doc" | "project"
    verified: bool
    origin: str = "db"                 # "db" | "web" | "llm" — 검증 출처 종류
    source_url: Optional[str] = None   # web origin일 때 SearchHit.url

class TaskItem(BaseModel):
    title: str
    skill: str
    resources: list[ResourceItem]
    est_hours: int
    verified: bool

class WeekPlan(BaseModel):
    week_index: int
    objectives: list[str]
    tasks: list[TaskItem]
    covered_skills: list[str]
    planned_hours: int                 # <= weekly_hours 검증 기준

class Roadmap(BaseModel):
    horizon: RoadmapHorizon
    total_weeks: int
    weeks: list[WeekPlan]
    weekly_hours_budget: int
    rationale: str                     # 기간 산출 근거(plan-and-solve)

# ── Critic ─────────────────────────────────────────────────
class Violation(BaseModel):
    type: ViolationType
    detail: str
    location: str

class CriticReport(BaseModel):
    verdict: CriticVerdict
    violations: list[Violation]        # pass면 빈 리스트
    checked_at_revision: int

# ── 툴 반환 ────────────────────────────────────────────────
class SkillRecord(BaseModel):
    name: str
    status: SkillStatus
    prereqs: list[str]
    resources: list[ResourceItem]
    typical_hours: int
    verified: bool

# ── 메모리 ─────────────────────────────────────────────────
class WeeklyProgress(BaseModel):
    week_index: int
    completed: bool
    note: Optional[str]

class EpisodicMemory(BaseModel):
    status: MemoryStatus
    last_roadmap: Optional[Roadmap]
    weekly_progress: list[WeeklyProgress]
    last_updated: str                  # ISO 타임스탬프

# ── 트레이스 ───────────────────────────────────────────────
class TraceEntry(BaseModel):
    node: str
    input_summary: str
    decision: Optional[str]           # node_decision enum 값
    tool_called: Optional[str]        # 예: "lookup_skill"
    output_summary: str
    ts: str                           # ISO 타임스탬프

# ── 최종 출력 ──────────────────────────────────────────────
class FinalOutput(BaseModel):
    profile: ProfileDiagnosis
    gap_analysis: GapAnalysis
    roadmap: Roadmap
    verified: bool
    trace_summary: list[TraceEntry]
    disclaimer: str                   # "이 결과는 합격·진로를 단정하지 않습니다."
```

---

## 4. 노드 목록과 역할

| 노드명 | 담당 에이전트/함수 | 읽는 State 키 | 쓰는 State 키 | 설명 |
|---|---|---|---|---|
| `onboarding_intake` | 구조화 함수 | — | `onboarding_input`, `episodic_memory`, `trace` | 프론트 폼 데이터를 `OnboardingInput`으로 파싱. `user_id`로 episodic_memory 조회해 State에 적재. 그래프 진입점. |
| `progress_reconciliation` | 메모리 반영 함수 | `episodic_memory` | `trace` (+ roadmap_plan 입력 컨텍스트) | returning_user면 미완료 주차 스킬 이월·완료 스킬 진척 반영. new_user면 pass-through. |
| `triage_router` | TriageRouter | `onboarding_input`, `clarify_answers` | `ambiguity_score`, `route_decision`, `trace` | 모호도 점수 산정 후 ask/proceed 결정. **conditional node**. |
| `clarify` | LLM 역질문 | `onboarding_input`, `ambiguity_score` | `clarify_answers`, `trace` | 2~3개 역질문 또는 유사직무 후보 제시. 사용자 응답을 `clarify_answers`에 누적. 응답 후 `triage_router`로 복귀. |
| `profile_diagnosis` | ProfileDiagnosisAgent | `onboarding_input`, `clarify_answers`, `episodic_memory` | `profile`, `trace` | 입력 외 추론 금지. 강점·약점·준비수준 구조화 출력. |
| `job_requirement` | JobRequirementAgent | `onboarding_input`, `rerun_reason`, `search_results`, `search_count` | `job_requirement`, `trace`, `search_results`, `search_count`, `search_degraded` | 공고 텍스트 → 필수/우대 역량 추출. `evidence_strength` 자가 표기. rerun 시 `rerun_reason` 컨텍스트 반영. 공고 부실(≤100자) 시 **노드 내부에서 `web_search` 호출**(ReAct: Act→Observe→extract), 각 스킬에 `source_url` 부착. |
| `gap_analysis` | GapRoadmapAgent (갭 단계) | `profile`, `job_requirement`, `search_results`, `search_count` | `gap_analysis`, `needs_rerun`, `rerun_reason`, `verified`, `trace`, `search_results`, `search_count`, `search_degraded` | 프로필 vs 직무요구 비교. `normalize_skill_name` + `lookup_skill` 호출로 스킬 상태 확인. status=unknown 시 **노드 내부에서 `web_search` 호출**로 실제 url 보강. job 근거 weak이면 `needs_rerun=true`. |
| `roadmap_plan` | GapRoadmapAgent (계획 단계) | `gap_analysis`, `episodic_memory`, `critic_report`, `search_results`, `search_count` | `roadmap`, `verified`, `trace`, `search_results`, `search_count`, `search_degraded` | `lookup_skill` 호출로 선후행·자원·시간 확정. status=unknown 스킬은 **노드 내부에서 `web_search` 호출**로 실제 url 보강(DB-miss 보강 검색). 갭 크기·`weekly_hours`로 동적 기간 산출(Plan-and-Solve). revise 시 위반사유 받아 재생성. |
| `roadmap_critic` | Critic 함수 | `roadmap`, `gap_analysis`, `onboarding_input` | `critic_report`, `revision_count`, `trace` | 4종 체크리스트 검증(상세는 §6). **conditional node**. |
| `trace_log` | 횡단 래퍼 | 각 노드 출력 | `trace` (append) | 노드 종료 시 `TraceEntry` append. 각 노드 래핑 또는 노드 내부에서 직접 호출. |
| `finalize` | 조립 함수 | `profile`, `gap_analysis`, `roadmap`, `critic_report`, `verified`, `trace`, `error` | `final_output` | `FinalOutput` 조립. `verified` 플래그·trace 요약·disclaimer 첨부. 그래프 종료점. |

---

## 5. 툴 계약 (Tool Contracts)

> **ReAct 패러다임**(Yao et al., 2022): 에이전트가 추론(Thought)과 행동(Act = 도구 호출)을 번갈아 수행해 외부 정보로 사실을 가져오고 환각을 줄입니다. CareerMate에서 `lookup_skill`(스킬 DB 조회)과 `web_search`(검색 API 호출)가 이 역할을 담당합니다. Act=`web_search` 호출 → Observe=snippet 파싱 → extract가 노드 본문 내부에서 순서대로 실행됩니다.

### 5-1. `lookup_skill`

```python
def lookup_skill(name: str) -> SkillRecord:
    """
    IT 직무 한정 정적 JSON 스킬 사전 조회.
    스킬명 → 선후행 관계·대표 학습자원·표준 소요시간 반환.

    on_fail: 사전 미존재 또는 IO 오류 시 throw 금지.
             status='unknown', prereqs=[], resources=[], typical_hours=0, verified=False 반환.
             호출자는 LLM 일반지식으로 폴백하되 해당 항목 verified=False 표기.
    """
    ...
```

**반환 예시 (known)**:
```json
{
  "name": "React",
  "status": "known",
  "prereqs": ["HTML", "CSS", "JavaScript"],
  "resources": [
    {"title": "React 공식 문서", "url": "https://react.dev", "type": "doc", "verified": true},
    {"title": "freeCodeCamp React 커리큘럼", "url": "https://www.freecodecamp.org/learn/front-end-development-libraries/", "type": "course", "verified": true}
  ],
  "typical_hours": 40,
  "verified": true
}
```

**반환 예시 (unknown)**:
```json
{
  "name": "SomeObscureLib",
  "status": "unknown",
  "prereqs": [],
  "resources": [],
  "typical_hours": 0,
  "verified": false
}
```

### 5-2. `list_skills_for_role`

```python
def list_skills_for_role(role: str) -> list[SkillRecord]:
    """
    직무명으로 관련 스킬 집합 일괄 조회.
    role 미매핑 시 빈 리스트 반환(throw 금지).
    """
    ...
```

### 5-3. `normalize_skill_name`

```python
def normalize_skill_name(raw: str) -> str:
    """
    자유표기 스킬명을 사전 표준 키로 매핑.
    예: 'react.js' → 'React', 'node' → 'Node.js'
    매칭 실패 시 raw 원문 그대로 반환(throw 금지).
    lookup_skill 적중률 향상용 전처리 헬퍼.
    """
    ...
```

### 5-4. `web_search`

```python
from tools.web_search import SearchHit

def web_search(query: str, k: int = 5) -> list[SearchHit]:
    """
    검색 API 1개(Tavily 또는 Serper 택1)를 호출해 상위 k개 결과를 반환.
    검색은 별도 ToolNode 분기 없이 노드 본문 내부 tool 호출로 수행(lookup_skill과 동일 방식).

    계약(lookup_skill과 동일 "절대 throw 금지" 철학):
      - 성공: SearchHit 리스트(0~k개). 각 항목은 url·snippet·retrieved_at 포함.
      - on_fail(API 키 없음/타임아웃/HTTP 오류/쿼터 초과/MAX_SEARCH 초과):
          빈 리스트 [] 반환 + 호출 노드가 state["search_degraded"]=True 설정.
          호출자는 LLM 자체지식으로 폴백하되 verified=False(origin="llm")로 표기.
      - 캐시 히트: state["search_results"][query] 반환(API 호출 없음, search_count 미증가).
      - 실제 API 호출 시 state["search_count"] += 1 후 MAX_SEARCH(=8) 초과면 빈 리스트 폴백.

    호출 위치:
      - job_requirement 노드: job_posting_text 부실 시 web_search로 required/preferred skills 보강.
      - roadmap_plan / gap_analysis 노드: lookup_skill 결과 status="unknown" 시에만 web_search 호출.
        (status="known"이면 DB 캐시 사용, 검색 생략.)
    """
    ...
```

> **크롤링 vs 검색 API**: `web_search`는 검색 API(Tavily/Serper)에 쿼리를 보내 **색인된 결과 메타데이터(title·url·snippet)** 만 수신합니다. 채용 사이트 HTML을 직접 fetch·파싱하는 크롤링과는 다른 행위입니다. `snippet`은 검색 API가 제공한 발췌이며, 우리 시스템이 대상 사이트에 직접 접속하지 않습니다.

---

## 6. Conditional Edge 조건 (의사코드)

### 6-1. Triage 분기 — `route_after_triage`

```python
AMBIGUITY_THRESHOLD = 0.6  # 조정 가능; 0.6 초과 시 ask

def route_after_triage(state: AgentState) -> str:
    """
    triage_router 노드 다음 분기.
    반환값: "clarify" | "profile_diagnosis"
    """
    if state["route_decision"] == "ask":
        return "clarify"
    return "profile_diagnosis"
```

> **설계 근거**: 7페이지 '직무 모호→유사직무', '정보 부족→추가질문'을 정식 라우터 엣지로 승격(피드백 제안1). Anthropic Building Effective Agents의 routing 패턴.

### 6-2. Gap→Job 되먹임 분기 — `route_after_gap`

```python
MAX_RERUN = 1  # 무한 루프 방지

def route_after_gap(state: AgentState) -> str:
    """
    gap_analysis 노드 다음 분기.
    반환값: "rerun_job" | "skip_rerun"

    주의: rerun_count += 1은 이 route 함수에서만 수행(CANON E).
          gap_analysis 노드 본문에서 증가하지 않는다.
    """
    if state["needs_rerun"] and state["rerun_count"] < MAX_RERUN:
        state["rerun_count"] += 1
        return "rerun_job"     # Gap→Job 되먹임(1회 한정)
    return "skip_rerun"
```

> **설계 근거**: 일방향 파이프라인을 양방향 협업으로 전환(피드백 §7). `rerun_count` 가드로 무한 루프 방지. 피드백 제안4(Gap→Job Re-query).

### 6-3. Critic 루프백 분기 — `route_after_critic`

```python
MAX_REVISIONS = 2  # 무한 루프 방지

def route_after_critic(state: AgentState) -> str:
    """
    roadmap_critic 노드 다음 분기.
    반환값: "revise" | "pass"

    주의: revision_count += 1은 이 route 함수에서만 수행(CANON E).
          roadmap_critic 노드 본문에서 증가하지 않는다.
    """
    if (state["critic_report"].verdict == "revise"
            and state["revision_count"] < MAX_REVISIONS):
        state["revision_count"] += 1
        return "revise"    # 위반 있음 → 재생성(최대 2회)
    return "pass"          # pass 또는 MAX_REVISIONS 도달 → 강제 finalize
```

> **설계 근거**: Reflexion(Shinn et al., 2023) 및 Self-Refine(Madaan et al., 2023)의 self-correction 루프. 가드레일(금칙 표현 검사)과 reflection을 한 노드에서 동시 구현(피드백 제안3). `revision_count` 가드로 무한 루프 방지.

### 6-4. Progress Reconciliation 분기 — `route_after_reconcile`

```python
def route_after_reconcile(state: AgentState) -> str:
    """
    progress_reconciliation 노드 다음 분기.
    반환값: 항상 "triage_router"
    (new_user/returning_user 공통. 처리 여부는 노드 내부에서 결정.)
    """
    return "triage_router"
```

---

## 7. Critic 체크리스트 (4종)

> `roadmap_critic` 노드가 실행하는 검증 규칙입니다. 위반 시 `Violation` 객체를 생성하고 `verdict="revise"`를 반환합니다. 이는 런타임 guardrail 구현으로, 프롬프트 지시만으로는 잘 새어나가는 가드레일을 코드 레벨에서 강제합니다(피드백 §6페이지).

```python
FORBIDDEN_PHRASES = [
    "합격 가능", "합격할 수 있", "취업 보장", "반드시 취업",
    "100% 합격", "성공 보장", "진로 결정"
]

def check_roadmap(state: AgentState) -> CriticReport:
    violations = []
    roadmap = state["roadmap"]
    gap = state["gap_analysis"]
    weekly_budget = state["onboarding_input"].weekly_hours

    # ① 부족역량 커버율: 모든 gap 스킬이 최소 1개 WeekPlan에 매핑
    covered = set()
    for week in roadmap.weeks:
        covered.update(week.covered_skills)
    for item in gap.gaps:
        if item.skill not in covered:
            violations.append(Violation(
                type=ViolationType.uncovered_gap,
                detail=f"{item.skill} 가 로드맵에 매핑되지 않음",
                location="roadmap.weeks"
            ))

    # ② 주차 시간 예산: planned_hours <= weekly_hours_budget
    for week in roadmap.weeks:
        if week.planned_hours > weekly_budget:
            violations.append(Violation(
                type=ViolationType.time_budget_exceeded,
                detail=f"{week.week_index}주차 {week.planned_hours}h > 예산 {weekly_budget}h",
                location=f"week {week.week_index}"
            ))

    # ③ 선후행 순서: prereq가 현재 주차보다 늦게 배치되면 위반
    skill_week: dict[str, int] = {}
    for week in roadmap.weeks:
        for skill in week.covered_skills:
            skill_week[skill] = week.week_index
    for week in roadmap.weeks:
        for skill in week.covered_skills:
            record = lookup_skill(normalize_skill_name(skill))
            for prereq in record.prereqs:
                if prereq in skill_week and skill_week[prereq] > week.week_index:
                    violations.append(Violation(
                        type=ViolationType.prereq_order_violation,
                        detail=f"{skill}의 선행인 {prereq}가 {skill_week[prereq]}주차에 배치(더 늦음)",
                        location=f"week {week.week_index}"
                    ))

    # ④ 금칙 표현: 로드맵 텍스트에 합격 단정 류 문구 없음
    roadmap_text = roadmap.model_dump_json()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in roadmap_text:
            violations.append(Violation(
                type=ViolationType.forbidden_phrase,
                detail=f"금칙 표현 발견: '{phrase}'",
                location="roadmap 텍스트"
            ))

    verdict = CriticVerdict.pass_ if not violations else CriticVerdict.revise
    return CriticReport(
        verdict=verdict,
        violations=violations,
        checked_at_revision=state["revision_count"]
    )
```

---

## 8. `progress_reconciliation` 노드 — 경량 Episodic 메모리

> 에이전트 메모리의 핵심은 '저장'이 아니라 **'과거를 반영해 현재 계획을 조정하는 것'** 입니다(피드백 §4). 이 노드는 DB 읽기+반영만 MVP에서 구현합니다.

```python
def progress_reconciliation(state: AgentState) -> AgentState:
    mem = state.get("episodic_memory")

    if mem is None or mem.status == MemoryStatus.new_user:
        # 신규 사용자: pass-through
        state["trace"].append(TraceEntry(
            node="progress_reconciliation",
            input_summary="신규 사용자",
            decision="skip_reconcile",
            tool_called=None,
            output_summary="episodic_memory 없음, 컨텍스트 주입 스킵",
            ts=now_iso()
        ))
        return state

    # returning_user: 이월·진척 컨텍스트 조립
    carry_over_skills = []   # 미완료 이월 대상
    completed_skills = []    # 완료 진척 반영 대상

    for prog in mem.weekly_progress:
        if not prog.completed and mem.last_roadmap:
            # 해당 주차의 covered_skills를 이월 대상으로 수집
            week = next(
                (w for w in mem.last_roadmap.weeks if w.week_index == prog.week_index),
                None
            )
            if week:
                carry_over_skills.extend(week.covered_skills)
        elif prog.completed and mem.last_roadmap:
            week = next(
                (w for w in mem.last_roadmap.weeks if w.week_index == prog.week_index),
                None
            )
            if week:
                completed_skills.extend(week.covered_skills)

    # 컨텍스트를 state에 주입 (roadmap_plan이 읽을 수 있도록)
    # 실제 구현에서는 별도 키(예: reconcile_context)나 onboarding_input.concern에 덧붙여 전달
    reconcile_context = {
        "carry_over_skills": list(set(carry_over_skills)),   # 이월: 다음 로드맵에 포함 필요
        "completed_skills": list(set(completed_skills)),     # 완료: 보유로 간주(우선순위 낮춤)
        "last_rationale": mem.last_roadmap.rationale if mem.last_roadmap else None
    }
    state["reconcile_context"] = reconcile_context  # type: ignore

    state["trace"].append(TraceEntry(
        node="progress_reconciliation",
        input_summary=f"이월 {len(carry_over_skills)}개 스킬, 완료 {len(completed_skills)}개 스킬",
        decision="reconcile",
        tool_called=None,
        output_summary=f"carry_over={carry_over_skills}, completed={completed_skills}",
        ts=now_iso()
    ))
    return state
```

**메모리 쓰기 (finalize 직후)**:
```python
def save_episodic_memory(user_id: str, new_roadmap: Roadmap):
    """
    finalize 완료 후 호출.
    last_roadmap 덮어쓰기(1개만 유지) + weekly_progress 초기화(completed=False).
    """
    db.upsert_last_roadmap(user_id, new_roadmap)
    db.seed_weekly_progress(user_id, [
        WeeklyProgress(week_index=w.week_index, completed=False, note=None)
        for w in new_roadmap.weeks
    ])
```

---

## 9. LangGraph 그래프 빌드 스케치

```python
from langgraph.graph import StateGraph, END

MAX_RERUN = 1
MAX_REVISIONS = 2
MAX_SEARCH = 8   # 세션당 누적 web_search 실제 API 호출 상한(캐시 히트 제외)

def build_career_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # ── 노드 등록 ───────────────────────────────────────────
    graph.add_node("onboarding_intake",          onboarding_intake)
    graph.add_node("progress_reconciliation",    progress_reconciliation)
    graph.add_node("triage_router",              triage_router)
    graph.add_node("clarify",                    clarify)
    graph.add_node("profile_diagnosis",          profile_diagnosis)
    graph.add_node("job_requirement",            job_requirement)
    graph.add_node("gap_analysis",               gap_analysis)
    graph.add_node("roadmap_plan",               roadmap_plan)
    graph.add_node("roadmap_critic",             roadmap_critic)
    graph.add_node("finalize",                   finalize)

    # ── 고정 엣지 ──────────────────────────────────────────
    graph.set_entry_point("onboarding_intake")
    graph.add_edge("onboarding_intake",       "progress_reconciliation")
    graph.add_edge("progress_reconciliation", "triage_router")
    graph.add_edge("clarify",                 "triage_router")   # clarify 후 재산정
    graph.add_edge("profile_diagnosis",       "job_requirement")
    graph.add_edge("job_requirement",         "gap_analysis")
    graph.add_edge("roadmap_plan",            "roadmap_critic")
    graph.add_edge("finalize",                END)

    # ── Conditional Edge 1: Triage 분기 ────────────────────
    graph.add_conditional_edges(
        "triage_router",
        route_after_triage,
        {
            "clarify":           "clarify",
            "profile_diagnosis": "profile_diagnosis",
        }
    )

    # ── Conditional Edge 2: Gap→Job 되먹임 ─────────────────
    graph.add_conditional_edges(
        "gap_analysis",
        route_after_gap,
        {
            "rerun_job":    "job_requirement",   # 되먹임(1회 한정)
            "skip_rerun":   "roadmap_plan",
        }
    )

    # ── Conditional Edge 3: Critic 루프백 ──────────────────
    graph.add_conditional_edges(
        "roadmap_critic",
        route_after_critic,
        {
            "revise":   "roadmap_plan",   # revise → 재생성(최대 2회)
            "pass":     "finalize",       # pass or MAX_REVISIONS → 종료
        }
    )

    return graph.compile()
```

---

## 10. Trace 로그 예시 (JSON)

대시보드의 'why-this-path' 타임라인으로 사용됩니다. 아래는 ask 경로로 분기했다가 proceed로 수렴한 뒤 Critic이 1회 revise한 케이스입니다.

```json
[
  {
    "node": "onboarding_intake",
    "input_summary": "user_id=u001, target_role='프론트엔드', weekly_hours=8",
    "decision": null,
    "tool_called": null,
    "output_summary": "OnboardingInput 구조화 완료, episodic_memory=None(신규)",
    "ts": "2025-10-01T09:00:00Z"
  },
  {
    "node": "progress_reconciliation",
    "input_summary": "new_user",
    "decision": "skip_reconcile",
    "tool_called": null,
    "output_summary": "신규 사용자, 이월 컨텍스트 없음",
    "ts": "2025-10-01T09:00:01Z"
  },
  {
    "node": "triage_router",
    "input_summary": "target_role='프론트엔드', owned_skills=['HTML']",
    "decision": "ask",
    "tool_called": null,
    "output_summary": "ambiguity_score=0.72 > threshold=0.6 → ask 분기",
    "ts": "2025-10-01T09:00:02Z"
  },
  {
    "node": "clarify",
    "input_summary": "역질문: React/Vue 중 어느 쪽 관심? 취업 목표 시점?",
    "decision": null,
    "tool_called": null,
    "output_summary": "clarify_answers 2개 수집",
    "ts": "2025-10-01T09:00:15Z"
  },
  {
    "node": "triage_router",
    "input_summary": "clarify_answers 반영 재산정",
    "decision": "proceed",
    "tool_called": null,
    "output_summary": "ambiguity_score=0.31 ≤ threshold → proceed",
    "ts": "2025-10-01T09:00:16Z"
  },
  {
    "node": "gap_analysis",
    "input_summary": "profile.weaknesses=['React','TypeScript'], job.required=['React','TypeScript','Git']",
    "decision": "skip_rerun",
    "tool_called": "lookup_skill",
    "output_summary": "gaps=[React(high), TypeScript(high), Git(medium)], evidence_strength=strong",
    "ts": "2025-10-01T09:00:25Z"
  },
  {
    "node": "roadmap_plan",
    "input_summary": "gaps 3개, weekly_hours=8, revision=0 — TypeScript status=unknown",
    "decision": null,
    "tool_called": "web_search(\"TypeScript 학습 강의 튜토리얼 공식문서\", k=3)",
    "output_summary": "SearchHit 3개 수신, ResourceItem origin=web url 보강 완료",
    "ts": "2025-10-01T09:00:30Z"
  },
  {
    "node": "roadmap_plan",
    "input_summary": "gaps 3개, weekly_hours=8, revision=0",
    "decision": null,
    "tool_called": "lookup_skill",
    "output_summary": "horizon=weeks_8, 8주 로드맵 생성",
    "ts": "2025-10-01T09:00:32Z"
  },
  {
    "node": "roadmap_critic",
    "input_summary": "revision_count=0",
    "decision": "revise",
    "tool_called": null,
    "output_summary": "violations=[time_budget_exceeded: 3주차 12h > 8h], verdict=revise",
    "ts": "2025-10-01T09:00:33Z"
  },
  {
    "node": "roadmap_plan",
    "input_summary": "위반사유: 3주차 시간 초과. revision_count=1",
    "decision": null,
    "tool_called": "lookup_skill",
    "output_summary": "3주차 planned_hours=8로 조정, 로드맵 재생성",
    "ts": "2025-10-01T09:00:40Z"
  },
  {
    "node": "roadmap_critic",
    "input_summary": "revision_count=1",
    "decision": "pass",
    "tool_called": null,
    "output_summary": "violations=[], verdict=pass → finalize",
    "ts": "2025-10-01T09:00:41Z"
  },
  {
    "node": "finalize",
    "input_summary": "verified=true, trace 10개",
    "decision": null,
    "tool_called": null,
    "output_summary": "FinalOutput 조립 완료",
    "ts": "2025-10-01T09:00:42Z"
  }
]
```

---

## 11. 에이전트다움의 증거 요약

이 그래프가 단순 프롬프트 체인(Anthropic 분류의 "workflow")과 다른 이유를 아래 표로 정리합니다.

| 에이전트 속성 | 구현 위치 | 근거 |
|---|---|---|
| **자율 라우팅** | `triage_router` conditional edge | Anthropic — routing pattern; 피드백 제안1 |
| **도구 호출 (tool use)** | `lookup_skill`, `list_skills_for_role`, `web_search` | ReAct (Yao et al., 2022); 피드백 제안2; Act=web_search→Observe=snippet 파싱 루프 |
| **자기 검증 / reflection** | `roadmap_critic` → `roadmap_plan` 루프 | Reflexion (Shinn et al., 2023); Self-Refine (Madaan et al., 2023); 피드백 제안3 |
| **런타임 가드레일** | Critic 4종 체크리스트 | 피드백 §4페이지·§6페이지 |
| **에이전트 간 되먹임** | `gap_analysis` → `job_requirement` 재요청 | 피드백 제안4; multi-agent 협업 |
| **동적 계획 수립** | `roadmap_plan` 기간 동적 산출 | Plan-and-Solve (Wang et al., 2023); 피드백 §4페이지 |
| **episodic 메모리** | `progress_reconciliation` 이월·진척 반영 | 피드백 제안5 |
| **실행 트레이스** | `trace` append-only 로그 | 피드백 제안6; agency 시각적 증명 |

---

## 관련 문서

- [00-overview.md](00-overview.md) — 프로젝트 개요 및 개선 방향
- [03-agent-contracts.md](03-agent-contracts.md) — 에이전트 I/O 계약 및 프롬프트 전략
- [04-tools-skill-db.md](04-tools-skill-db.md) — 스킬 DB JSON 사전 및 툴 구현
- [06-data-model.md](06-data-model.md) — Pydantic 모델·데이터 스키마·메모리·trace
