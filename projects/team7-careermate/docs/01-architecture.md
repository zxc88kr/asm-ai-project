# 시스템 아키텍처

이 문서는 CareerMate의 전체 시스템 구성과 컴포넌트 책임을 설명합니다.
어디서 LLM이 호출되고 어디서 코드/툴이 실행되는지를 명확히 구분해, 학생이 구현 우선순위를 잡을 수 있도록 작성했습니다.

---

## 1. 상위 아키텍처 개요

CareerMate는 네 계층으로 구성됩니다.

```
┌─────────────────────────────────────────────────────────────┐
│                        React 프론트엔드                      │
│   [온보딩 입력 패널]  [로드맵 대시보드 패널]  [트레이스 패널] │
│         ↕ HTTP POST /run                ↕ GET /status        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI 백엔드 서버                      │
│  /run → graph.invoke()   /status → state 조회               │
│  episodic memory R/W (JSON 파일 or SQLite)                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               LangGraph 상태 그래프 (에이전트 런타임)         │
│                                                             │
│  START → onboarding_intake → progress_reconciliation        │
│        → triage_router ──ask──→ clarify ──┐                 │
│                         └proceed─┘         │(루프백)        │
│        → profile_diagnosis                 │                │
│        → job_requirement ◀──────────────────── gap_analysis │
│        → gap_analysis ──needs_rerun──▶ job_requirement       │
│        → roadmap_plan ◀──────────────── roadmap_critic       │
│        → roadmap_critic ──pass──▶ finalize → END            │
└─────────────────────────────────────────────────────────────┘
                            │
          ┌─────────────────┼──────────────────┐
          ▼                 ▼                  ▼
┌──────────────────┐ ┌─────────────────────┐ ┌────────────────────────────────┐
│   LLM API        │ │  웹검색 API (외부)   │ │   Skill DB (정적 JSON/CSV)      │
│ (Claude / GPT 등)│ │ (검색만/크롤링 아님) │ │   skill_db.json                 │
│ 노드별 프롬프트   │ │  web_search 툴 호출  │ │   lookup_skill(name) 함수 호출  │
│ 호출             │ │  결과 파싱은 노드 LLM│ │   (캐시/보조, DB-miss 시 검색)  │
└──────────────────┘ └─────────────────────┘ └────────────────────────────────┘
```

---

## 2. 컴포넌트 책임 표

| 컴포넌트 | 역할 | LLM 호출 여부 |
|----------|------|--------------|
| **React 프론트엔드** | 온보딩 폼 입력 수집, 로드맵 렌더링, 트레이스 타임라인 표시, 주차 완료 체크박스 | 없음 (코드만) |
| **FastAPI 백엔드** | HTTP 요청 수신, `graph.invoke()` 호출, episodic memory(JSON/SQLite) R/W, 응답 직렬화 | 없음 (코드만) |
| **LangGraph 상태 그래프** | 노드 실행 순서 제어, conditional edge로 라우팅·루프 관리, `AgentState` 전달 | 노드 내부에서 발생 |
| **TriageRouter 노드** | `ambiguity_score` 산정 후 `ask`/`proceed` 분기 | **LLM 호출** |
| **clarify 노드** | 역질문 2~3개 생성 또는 유사직무 후보 제시 | **LLM 호출** |
| **profile_diagnosis 노드** | 온보딩 입력 기반 강점/약점/준비수준 구조화 | **LLM 호출** |
| **job_requirement 노드** | 공고 텍스트 파싱, evidence_strength 자가 표기 | **LLM 호출** |
| **gap_analysis 노드** | profile vs job_requirement 비교, needs_rerun 판단 | **LLM 호출** |
| **roadmap_plan 노드** | `lookup_skill` 툴 호출 후 동적 주차 로드맵 생성 | **LLM 호출 + 툴 호출** |
| **roadmap_critic 노드** | 4종 체크리스트 검증, `pass`/`revise` 판정 | **LLM 호출** (또는 코드 검증) |
| **progress_reconciliation 노드** | episodic memory 읽기, 미완료 이월·완료 진척 반영 | 없음 (코드만) |
| **finalize 노드** | `FinalOutput` 조립, trace 요약 첨부, verified 플래그 설정 | 없음 (코드만) |
| **lookup_skill 툴** | 정적 JSON 사전 조회, `SkillRecord` 반환 (캐시/보조 역할: Agent3 DB-miss 시 web_search로 보강) | **없음 (코드만)** — 이것이 tool use의 핵심 |
| **web_search 툴** | 검색 API(Tavily/Serper) 호출, `SearchHit` 리스트 반환, 결과 파싱은 호출 노드 LLM이 담당 (크롤링 아님) | **없음 (코드만)** — 검색 API 호출 어댑터 |
| **Skill DB (JSON)** | IT 직무 50~150행 스킬 사전: prereqs, resources, typical_hours | 없음 (데이터) |
| **웹검색 API (외부)** | 검색 엔진(Tavily 또는 Serper)이 색인한 결과 메타데이터(title·url·snippet) 제공. 우리 시스템은 대상 사이트에 직접 접속하지 않음 | 없음 (외부 서비스) |

> **하이브리드 구조 요점:** LLM은 추론이 필요한 노드(진단·분석·생성)에서만 호출됩니다.
> 스킬 조회(`lookup_skill`), 검색 API 호출(`web_search`), 라우팅 엣지 평가, 시간 예산 검증, trace append는 모두 결정론적 코드로 처리합니다.
> 외부 호출은 **LLM 추론 + 검색 API** 두 종류입니다. 이 분리가 없으면 환각과 불확실성이 전체 파이프라인으로 전파됩니다 (ReAct, Yao et al. 2022).
>
> **크롤링 vs 검색 경계:** 실시간 **크롤링**(사이트 직접 순회·HTML 수집)은 제외하되, **검색 API 호출**(쿼리→색인된 결과 메타데이터 수신)은 도입한다. 둘은 다른 행위다.

---

## 3. 데이터 흐름 (요청 1회 기준)

```
사용자 입력 (OnboardingInput)
        │
        ▼
[FastAPI] /run 수신
        │
        ▼
[onboarding_intake]
  - OnboardingInput 구조화
  - user_id로 episodic memory 조회
  - EpisodicMemory → state.episodic_memory
        │
        ▼
[progress_reconciliation]  ← 재방문자만 동작 (코드)
  - completed 주차 스킬 → 보유로 간주
  - 미완료 주차 스킬 → 이월 대상으로 컨텍스트 주입
        │
        ▼
[triage_router]  ← LLM: ambiguity_score 산정
  - score > AMBIGUITY_THRESHOLD → route_decision = "ask"
  - score ≤ AMBIGUITY_THRESHOLD → route_decision = "proceed"
        │
   ask ─┤─ proceed
        │         │
        ▼         │
  [clarify]       │
  - 역질문 생성   │  ← LLM
  - 응답 수집     │
  → triage_router │  (재산정, 보통 proceed로 수렴)
                  │
                  ▼
        [profile_diagnosis]  ← LLM
          - profile 생성
                  │
                  ▼
        [job_requirement]  ← LLM
          - job_requirement 추출
          - evidence_strength 자가 표기
                  │
                  ▼
        [gap_analysis]  ← LLM
          - 부족역량·우선순위 도출
          - needs_rerun 판단
                  │
        needs_rerun=true ─────▶ [job_requirement] 재실행 (최대 1회)
        needs_rerun=false
                  │
                  ▼
        [roadmap_plan]  ← LLM + lookup_skill 툴 호출
          - lookup_skill(skill_name) → SkillRecord
          - 선후행·자원·시간 확정 후 주차 로드맵 생성
                  │
                  ▼
        [roadmap_critic]  ← LLM (또는 코드 기반 검증)
          체크리스트 4종:
          ① 모든 gap.skill이 1개 이상 주차에 mapped
          ② 각 주차 week.planned_hours ≤ weekly_hours_budget (주차별 기준)
          ③ prereq_order 위반 없음 (lookup_skill.prereqs 기준)
          ④ 금칙표현("합격 가능", "반드시 취업") 없음
                  │
        revise ───┤─── pass
                  │          │
    (최대 2회)    ▼          ▼
        [roadmap_plan]   [finalize]  ← 코드
        재생성           - FinalOutput 조립
                         - verified 플래그
                         - trace 요약
                              │
                              ▼
                   [FastAPI] 응답 직렬화 → React 렌더링
```

---

## 4. LangGraph 상태 그래프 구조

LangGraph는 노드(함수)와 엣지(연결·조건)로 에이전트 제어 흐름을 표현합니다.
조건부 엣지(conditional edge)가 라우팅·루프를 가능하게 합니다 (LangGraph 공식 문서).

### 4-1. State 스키마 (핵심 필드)

```python
from typing import TypedDict, Optional
from pydantic import BaseModel

class AgentState(TypedDict):
    # 식별
    user_id: str
    session_id: str

    # 입력
    onboarding_input: OnboardingInput
    clarify_answers: list[ClarifyAnswer]    # ask 경로에서만 채워짐

    # 라우팅
    ambiguity_score: float                  # 0.0~1.0
    route_decision: str                     # "ask" | "proceed"

    # 에이전트 출력
    profile: Optional[ProfileDiagnosis]
    job_requirement: Optional[JobRequirement]
    gap_analysis: Optional[GapAnalysis]
    roadmap: Optional[Roadmap]
    critic_report: Optional[CriticReport]

    # 되먹임 제어
    needs_rerun: bool
    rerun_reason: Optional[str]
    rerun_count: int                        # MAX_RERUN = 1
    revision_count: int                     # MAX_REVISIONS = 2

    # 메모리
    episodic_memory: Optional[EpisodicMemory]

    # 웹검색
    search_results: dict[str, list[SearchHit]]  # query→SearchHit 리스트 캐시(세션 내)
    search_count: int                           # 세션 누적 web_search 실제 API 호출 횟수
    search_degraded: bool                       # 검색 실패/상한 초과 시 True

    # 횡단 관심사
    trace: list[TraceEntry]                 # append-only
    verified: bool
    final_output: Optional[FinalOutput]
    error: Optional[str]
```

### 4-2. 그래프 정의 의사코드

```python
from langgraph.graph import StateGraph, END

AMBIGUITY_THRESHOLD = 0.6
MAX_RERUN = 1
MAX_REVISIONS = 2
MAX_SEARCH = 8

def build_graph() -> StateGraph:
    g = StateGraph(AgentState)

    # 노드 등록
    g.add_node("onboarding_intake",        onboarding_intake_fn)
    g.add_node("progress_reconciliation",  progress_reconciliation_fn)
    g.add_node("triage_router",            triage_router_fn)
    g.add_node("clarify",                  clarify_fn)
    g.add_node("profile_diagnosis",        profile_diagnosis_fn)
    g.add_node("job_requirement",          job_requirement_fn)
    g.add_node("gap_analysis",             gap_analysis_fn)
    g.add_node("roadmap_plan",             roadmap_plan_fn)
    g.add_node("roadmap_critic",           roadmap_critic_fn)
    g.add_node("finalize",                 finalize_fn)

    # 고정 엣지
    g.set_entry_point("onboarding_intake")
    g.add_edge("onboarding_intake",       "progress_reconciliation")
    g.add_edge("progress_reconciliation", "triage_router")
    g.add_edge("clarify",                 "triage_router")   # 역질문 후 재산정
    g.add_edge("profile_diagnosis",       "job_requirement")
    g.add_edge("job_requirement",         "gap_analysis")
    g.add_edge("roadmap_plan",            "roadmap_critic")
    g.add_edge("finalize",                END)

    # 조건부 엣지 1: 모호성 라우터 (피드백 제안 1)
    g.add_conditional_edges(
        "triage_router",
        lambda s: s["route_decision"],
        {"ask": "clarify", "proceed": "profile_diagnosis"}
    )

    # 조건부 엣지 2: Gap→Job 되먹임 (피드백 제안 4)
    g.add_conditional_edges(
        "gap_analysis",
        lambda s: "rerun_job" if (s["needs_rerun"] and s["rerun_count"] < MAX_RERUN)
                  else "skip_rerun",
        {"rerun_job": "job_requirement", "skip_rerun": "roadmap_plan"}
    )

    # 조건부 엣지 3: Critic 재생성 루프 (피드백 제안 3)
    g.add_conditional_edges(
        "roadmap_critic",
        lambda s: "revise" if (s["critic_report"].verdict == "revise"
                               and s["revision_count"] < MAX_REVISIONS)
                  else "finalize",
        {"revise": "roadmap_plan", "finalize": "finalize"}
    )

    return g.compile()
```

---

## 5. 툴: lookup_skill (Skill DB 조회)

LLM 단독 호출이 아니라 함수 호출로 스킬 정보를 가져옵니다.
이것이 "프롬프트 체인"을 "에이전트"로 바꾸는 핵심 장치입니다 (ReAct, Yao et al. 2022).

### 5-1. 툴 시그니처

```python
def lookup_skill(name: str) -> SkillRecord:
    """
    IT 직무용 정적 JSON 사전에서 스킬 정보를 조회합니다.
    사전에 없으면 status='unknown' 폴백 레코드를 반환합니다.
    예외/IO 오류도 unknown 폴백으로 처리합니다 (raise 금지).
    """
    ...

def list_skills_for_role(role: str) -> list[SkillRecord]:
    """직무명으로 관련 스킬 집합 일괄 조회. 없으면 빈 리스트 반환."""
    ...

def normalize_skill_name(raw: str) -> str:
    """
    자유 표기("react.js") → 사전 표준키("React").
    매칭 실패 시 원문 그대로 반환.
    """
    ...
```

### 5-2. SkillRecord 반환 예시 (JSON)

```json
{
  "name": "React",
  "status": "known",
  "prereqs": ["HTML", "CSS", "JavaScript"],
  "resources": [
    {
      "title": "React 공식 문서",
      "url": "https://react.dev/learn",
      "type": "doc",
      "verified": true
    },
    {
      "title": "노마드코더 React 강의",
      "url": null,
      "type": "course",
      "verified": false
    }
  ],
  "typical_hours": 40,
  "verified": true
}
```

### 5-3. 폴백 처리 (unknown 스킬)

```python
# lookup_skill이 unknown을 반환할 때 호출자 처리 예시
record = lookup_skill(normalize_skill_name("ReactNative"))
if record.status == "unknown":
    # LLM 일반지식으로 fallback
    resources = llm_generate_resources(skill_name)
    # 해당 항목에 verified=false 마킹
    state["verified"] = False
```

### 5-4. Skill DB JSON 구조 (50~150행 예시)

```json
{
  "skills": {
    "Python": {
      "prereqs": [],
      "resources": [
        {"title": "Python 공식 튜토리얼", "url": "https://docs.python.org/ko/3/tutorial/", "type": "doc", "verified": true}
      ],
      "typical_hours": 30
    },
    "FastAPI": {
      "prereqs": ["Python"],
      "resources": [
        {"title": "FastAPI 공식 문서", "url": "https://fastapi.tiangolo.com/ko/", "type": "doc", "verified": true}
      ],
      "typical_hours": 20
    },
    "React": {
      "prereqs": ["HTML", "CSS", "JavaScript"],
      "resources": [
        {"title": "React 공식 문서", "url": "https://react.dev/learn", "type": "doc", "verified": true}
      ],
      "typical_hours": 40
    },
    "SQL": {
      "prereqs": [],
      "resources": [
        {"title": "SQLZoo", "url": "https://sqlzoo.net/", "type": "course", "verified": true}
      ],
      "typical_hours": 20
    }
  },
  "role_skill_map": {
    "백엔드 개발자": ["Python", "FastAPI", "SQL", "Docker"],
    "프론트엔드 개발자": ["HTML", "CSS", "JavaScript", "React"]
  },
  "aliases": {
    "react.js": "React",
    "py": "Python",
    "fast api": "FastAPI"
  }
}
```

---

## 6. 실행 트레이스 (trace_log)

각 노드 종료 시 `TraceEntry`를 `state["trace"]`에 append합니다.
대시보드 '에이전트가 거친 경로' 타임라인의 원천 데이터입니다.

```python
from datetime import datetime, timezone

def append_trace(state: AgentState, entry: dict) -> None:
    """노드 종료 시 호출. state["trace"]에 append만 함(수정 금지)."""
    state["trace"].append(TraceEntry(
        node=entry["node"],
        input_summary=entry["input_summary"],
        decision=entry.get("decision"),          # 라우터/critic/되먹임만
        tool_called=entry.get("tool_called"),    # 예: "lookup_skill"
        output_summary=entry["output_summary"],
        ts=datetime.now(timezone.utc).isoformat()
    ))
```

**트레이스 출력 예시 (타임라인):**

| # | node | decision | tool_called | output_summary |
|---|------|----------|-------------|----------------|
| 1 | triage_router | ask | — | ambiguity_score=0.8, 역질문 2개 발송 |
| 2 | clarify | — | — | 목표직무 "프론트엔드 개발자"로 확정 |
| 3 | triage_router | proceed | — | ambiguity_score=0.3, proceed |
| 4 | profile_diagnosis | — | — | 강점: JavaScript, 약점: React·SQL |
| 5 | job_requirement | — | — | evidence_strength=weak |
| 6 | gap_analysis | rerun_job | — | needs_rerun=true, "공고 너무 짧음" |
| 7 | job_requirement | — | — | evidence_strength=strong (재추출) |
| 8 | gap_analysis | roadmap_plan | — | 부족스킬: React·SQL·TypeScript |
| 9 | roadmap_plan | — | lookup_skill | React·SQL 스킬 레코드 확정 |
| 10 | roadmap_critic | revise | — | time_budget_exceeded: week3=12h > 8h |
| 11 | roadmap_plan | — | lookup_skill | 재생성 (revision_count=1) |
| 12 | roadmap_critic | pass | — | 체크리스트 4종 통과 |
| 13 | finalize | — | — | FinalOutput 조립, verified=true |

---

## 7. episodic 메모리 저장 구조

재방문 사용자의 직전 로드맵과 주차 진행 기록을 저장합니다.
MVP에서는 JSON 파일 또는 SQLite 2테이블로 구현합니다.

```
# 개념적 테이블 구조 (SQLite 또는 JSON)

last_roadmap 테이블:
  user_id (PK)  |  roadmap_json  |  updated_at
  "user_001"    |  {...}         |  "2025-05-20T10:00:00Z"

weekly_progress 테이블:
  user_id  |  week_index  |  completed  |  note
  "user_001" |  1          |  true       |  "React 기초 완료"
  "user_001" |  2          |  false      |  null
  "user_001" |  3          |  false      |  null
```

```python
# onboarding_intake에서 호출
def load_episodic_memory(user_id: str) -> EpisodicMemory:
    record = db.query(user_id)
    if not record:
        return EpisodicMemory(
            status="new_user",
            last_roadmap=None,
            weekly_progress=[],
            last_updated=""
        )
    return EpisodicMemory(
        status="returning_user",
        last_roadmap=Roadmap(**record["roadmap_json"]),
        weekly_progress=[WeeklyProgress(**p) for p in record["weekly_progress"]],
        last_updated=record["updated_at"]
    )

# progress_reconciliation 노드 핵심 로직
def progress_reconciliation_fn(state: AgentState) -> AgentState:
    mem = state.get("episodic_memory")
    if not mem or mem.status == "new_user":
        append_trace(state, {"node": "progress_reconciliation",
                             "decision": "skip_reconcile", ...})
        return state

    # 미완료 주차 스킬 → 이월 대상
    carry_over = [s for w in mem.weekly_progress
                  if not w.completed
                  for s in get_covered_skills(w.week_index, mem.last_roadmap)]

    # 완료 주차 스킬 → 보유로 간주 (약점 우선순위 하향)
    completed = [s for w in mem.weekly_progress
                 if w.completed
                 for s in get_covered_skills(w.week_index, mem.last_roadmap)]

    # roadmap_plan 입력 컨텍스트로 주입 (state에 메타데이터 추가)
    state["episodic_memory"].carry_over_skills = carry_over
    state["episodic_memory"].completed_skills  = completed

    append_trace(state, {"node": "progress_reconciliation",
                         "decision": "reconcile",
                         "output_summary": f"이월 {len(carry_over)}개, 완료 {len(completed)}개"})
    return state
```

---

## 8. 에이전트 vs 코드 분류 요약

이 표는 "어디가 LLM이고 어디가 코드인가"를 한 눈에 정리합니다.
LLM 비용과 환각 리스크는 LLM 호출 노드에만 존재합니다.

| 계층 | 실행 주체 | 근거 |
|------|-----------|------|
| onboarding_intake | 코드 (Pydantic 파싱 + DB 조회) | 구조화·조회는 결정론적 처리 |
| triage_router | **LLM** | ambiguity 판단은 자연어 추론 필요 |
| clarify | **LLM** | 역질문 생성은 자연어 생성 필요 |
| progress_reconciliation | 코드 (리스트 연산) | 완료/미완료 집계는 결정론적 |
| profile_diagnosis | **LLM** | 역량 해석·구조화는 추론 필요 |
| job_requirement | **LLM** | 공고 파싱·evidence 판단은 추론 필요 |
| gap_analysis | **LLM** | profile vs job 비교·우선순위는 추론 필요 |
| lookup_skill | **코드** (JSON 조회) | 사전 조회는 결정론적 — tool use의 핵심 (캐시/보조 역할) |
| web_search | **코드** (검색 API 호출) | 검색 API 어댑터는 코드, 결과 파싱은 노드 LLM |
| roadmap_plan | **LLM** + lookup_skill / web_search 툴 | 계획 생성은 추론, 자원 조회는 툴 |
| roadmap_critic | **LLM** 또는 코드 혼합 | ①②③ 수치 검증은 코드, ④ 금칙어는 LLM |
| finalize | 코드 (조립) | 데이터 집계·플래그 설정은 결정론적 |
| trace_log | 코드 (append) | 로그 기록은 결정론적 |

> **구현 조언:** roadmap_critic의 체크리스트 ①②③은 LLM 없이 Python 코드로 검증하면
> 비용을 아끼고 결과를 확정적으로 만들 수 있습니다.
> ④ 금칙표현은 정규식 또는 LLM 판단 중 선택할 수 있습니다.
> Self-Refine (Madaan et al. 2023)에서 제안하듯, 동일 모델이 자기 출력을 평가해도 충분합니다.

---

## 9. 1.5주 구현 우선순위

피드백이 지목한 3대 개선을 LangGraph 그래프 관점에서 정리합니다.

| 우선순위 | 구현 항목 | 해당 노드/엣지 | 에이전트 요건 충족 |
|---------|-----------|---------------|--------------------|
| **1** | 모호성 라우터 | `triage_router` + `clarify` + conditional_edge | 자율 라우팅 |
| **2** | Critic 재생성 루프 | `roadmap_critic` + conditional_edge | reflection + guardrails |
| **3** | Skill DB 조회 툴 | `lookup_skill` + `skill_db.json` + roadmap_plan 연결 | tool use |
| 4 | Gap→Job 되먹임 | `gap_analysis` conditional_edge | multi-agent 협업 |
| 5 | episodic 메모리 반영 | `progress_reconciliation` + DB R/W | 에이전트 메모리 |
| 6 | trace 타임라인 | `trace_log` + 대시보드 패널 | agency 가시화 |

---

## 관련 문서

- [에이전트 그래프 상세](02-agent-graph.md) — 각 노드 프롬프트 계약, 입출력 스키마
- [툴·Skill DB 명세](04-tools-skill-db.md) — JSON 스킬 사전 구조, lookup_skill·web_search 툴 계약
- [Pydantic 모델 정의](06-data-model.md) — State, SkillRecord, SearchHit 등 전체 모델

---

## 참고 문헌

- Anthropic, *Building Effective Agents* (2024) — workflow vs agent 구분, routing/evaluator-optimizer 패턴
- Yao et al., *ReAct: Synergizing Reasoning and Acting in LMs* (2022) — 툴 호출로 환각 억제
- Shinn et al., *Reflexion* (2023) — 언어 피드백 기반 self-reflection 루프
- Madaan et al., *Self-Refine* (2023) — 단일 모델 자기 개선 루프
- Wang et al., *Plan-and-Solve Prompting* (2023) — 동적 task decomposition
- LangGraph Documentation, *Conditional Edges & Graph State* (LangChain) — 조건 엣지·루프 구현
