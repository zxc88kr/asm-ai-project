# 08. 1.5주 구현 플랜

이 문서는 남은 약 1.5주(~10일)를 일자별·마일스톤으로 정리한 실행 계획입니다.
피드백 핵심 3개(모호성 라우터 / Critic 루프 / 스킬 DB)를 중심으로 그래프 골격을 먼저 세우고, 노드 내부를 채우는 순서로 진행합니다.

---

## 0. 전체 타임라인 한눈에 보기

```
Day 1-2   │ M1: 그래프 골격 + 상태 스키마
Day 3     │ M2: 스킬 DB + lookup_skill 툴 + web_search 어댑터(검색 API 1개) 0.5일
Day 4-5   │ M3: 모호성 라우터 + clarify 노드
Day 6-7   │ M4: 핵심 에이전트 노드 (Profile / Job / Gap) + Agent2·3 web_search 통합
Day 8-9   │ M5: roadmap_plan + roadmap_critic 루프
Day 10    │ M6: episodic 메모리 + trace + 통합 테스트
```

> **우선순위 원칙:** LangGraph 그래프 정의(노드·조건 엣지·상태 스키마)와 툴/검증 함수 구현이 프론트엔드·백엔드보다 먼저입니다 (feedback.md 1.5주 조언).

---

## 1. 마일스톤별 상세 계획

### M1 (Day 1-2): 그래프 골격 + 상태 스키마

**목표:** 노드 내부가 stub이어도 그래프가 실행되고 조건 엣지가 동작하는 상태.

#### 1-1. State 스키마 정의

```python
# careermate/state.py
from __future__ import annotations
from typing import Annotated
import operator
from pydantic import BaseModel, Field

# --- enum 값 (문자열 상수로 선언) ---
# route_decision: "ask" | "proceed"
# critic_verdict:  "pass" | "revise"
# skill_status:    "known" | "unknown"
# evidence_strength: "strong" | "weak"
# memory_status:   "new_user" | "returning_user"

class AgentState(BaseModel):
    user_id: str
    session_id: str
    onboarding_input: OnboardingInput | None = None
    clarify_answers: list[ClarifyAnswer] = Field(default_factory=list)
    ambiguity_score: float = 0.0
    route_decision: str = "proceed"          # "ask" | "proceed"
    profile: ProfileDiagnosis | None = None
    job_requirement: JobRequirement | None = None
    gap_analysis: GapAnalysis | None = None
    roadmap: Roadmap | None = None
    critic_report: CriticReport | None = None
    needs_rerun: bool = False
    rerun_reason: str | None = None
    rerun_count: int = 0
    revision_count: int = 0
    episodic_memory: EpisodicMemory | None = None
    trace: Annotated[list[TraceEntry], operator.add] = Field(default_factory=list)
    verified: bool = True
    final_output: FinalOutput | None = None
    error: str | None = None
```

> `trace` 필드에 `Annotated[list, operator.add]`를 쓰면 LangGraph가 여러 노드의 append 결과를 자동 병합합니다.

#### 1-2. 그래프 골격 (stub 노드)

```python
# careermate/graph.py
from langgraph.graph import StateGraph, START, END
from .state import AgentState

MAX_RERUN = 1
MAX_REVISIONS = 2
MAX_SEARCH = 8   # 세션당 누적 web_search 실제 API 호출 상한(캐시 히트 제외)

def build_graph() -> StateGraph:
    g = StateGraph(AgentState)

    # 노드 등록 (내부는 stub → 이후 채움)
    g.add_node("onboarding_intake",       stub_node)
    g.add_node("progress_reconciliation", stub_node)
    g.add_node("triage_router",           stub_node)
    g.add_node("clarify",                 stub_node)
    g.add_node("profile_diagnosis",       stub_node)
    g.add_node("job_requirement",         stub_node)
    g.add_node("gap_analysis",            stub_node)
    g.add_node("roadmap_plan",            stub_node)
    g.add_node("roadmap_critic",          stub_node)
    g.add_node("finalize",                stub_node)

    # 고정 엣지
    g.add_edge(START,                    "onboarding_intake")
    g.add_edge("onboarding_intake",      "progress_reconciliation")
    g.add_edge("progress_reconciliation","triage_router")
    g.add_edge("clarify",                "triage_router")   # ask 후 재산정
    g.add_edge("profile_diagnosis",      "job_requirement")
    g.add_edge("job_requirement",        "gap_analysis")
    g.add_edge("roadmap_plan",           "roadmap_critic")
    g.add_edge("finalize",               END)

    # 조건 엣지
    g.add_conditional_edges(
        "triage_router",
        lambda s: s.route_decision,          # "ask" | "proceed"
        {"ask": "clarify", "proceed": "profile_diagnosis"},
    )
    g.add_conditional_edges(
        "gap_analysis",
        _gap_router,
        {"rerun_job": "job_requirement", "skip_rerun": "roadmap_plan"},
    )
    g.add_conditional_edges(
        "roadmap_critic",
        _critic_router,
        {"revise": "roadmap_plan", "pass": "finalize"},
    )
    return g.compile()

def _gap_router(s: AgentState) -> str:
    if s.needs_rerun and s.rerun_count < MAX_RERUN:
        return "rerun_job"
    return "skip_rerun"

def _critic_router(s: AgentState) -> str:
    if (s.critic_report and s.critic_report.verdict == "revise"
            and s.revision_count < MAX_REVISIONS):
        return "revise"
    return "pass"
```

**Day 1 확인 체크포인트:**
- `build_graph()` 호출 시 예외 없음
- stub 상태로 `graph.invoke({...})` 가 START→END 완주
- 조건 엣지 3개의 분기 경로가 print로 확인됨

---

### M2 (Day 3): 스킬 DB + lookup_skill 툴 + web_search 어댑터

**목표:** tool use 0 → 2. LLM 환각 없이 스킬 → 선후행·자원·시간을 함수로 조회 + 검색 API 1개(Tavily 또는 Serper) 어댑터 추가.

이 작업을 스킬 DB부터 시작하는 이유: 스킬 DB가 없으면 roadmap_plan·roadmap_critic 둘 다 구현 불가. 또한 Claude Code로 JSON을 미리 만들어두면 이후 노드 테스트가 쉬워집니다.

> **스킬 DB 위치:** `lookup_skill`(스킬 DB)은 사람이 url을 직접 검수한 고품질 **정적 캐시**입니다. Agent3(roadmap_plan/gap_analysis)는 DB-known이면 검색 생략, DB-unknown이면 `web_search`로 실제 url을 보강합니다. Agent2(job_requirement)는 웹검색을 기본 의존하고 DB는 보조 검증용으로만 사용합니다.

> **web_search 어댑터(0.5일):** `tools/web_search.py` 단일 파일에 `web_search()` 1함수 + 세션 캐시 dict + `MAX_SEARCH=8` 가드. 검색 API 실패 시 빈 리스트 반환(throw 금지, lookup_skill on_fail과 동일 철학). 결과 파싱은 호출 노드의 LLM이 담당(별도 파서 코드 불필요).

#### 2-1. 스킬 사전 JSON (50~150행, IT 직무 1~2개 한정)

```json
// careermate/data/skill_db.json  (발췌, 실제 50+ 행)
{
  "Python": {
    "prereqs": [],
    "resources": [
      {"title": "점프 투 파이썬",      "url": "https://wikidocs.net/book/1",   "type": "doc",    "verified": true},
      {"title": "Python 공식 튜토리얼","url": "https://docs.python.org/ko/3/", "type": "doc",    "verified": true}
    ],
    "typical_hours": 40
  },
  "FastAPI": {
    "prereqs": ["Python"],
    "resources": [
      {"title": "FastAPI 공식 문서", "url": "https://fastapi.tiangolo.com/ko/", "type": "doc", "verified": true}
    ],
    "typical_hours": 20
  },
  "React": {
    "prereqs": ["JavaScript"],
    "resources": [
      {"title": "React 공식 문서", "url": "https://ko.react.dev/", "type": "doc", "verified": true}
    ],
    "typical_hours": 30
  },
  "SQL": {
    "prereqs": [],
    "resources": [
      {"title": "SQLZoo", "url": "https://sqlzoo.net/", "type": "course", "verified": true}
    ],
    "typical_hours": 15
  },
  "Linux 기초": {
    "prereqs": [],
    "resources": [
      {"title": "The Linux Command Line (무료 PDF)", "url": "https://linuxcommand.org/tlcl.php", "type": "doc", "verified": true}
    ],
    "typical_hours": 10
  },
  "Docker": {
    "prereqs": ["Linux 기초"],
    "resources": [
      {"title": "Docker 공식 문서", "url": "https://docs.docker.com/get-started/", "type": "doc", "verified": true}
    ],
    "typical_hours": 15
  }
}
```

> 직무별 스킬 매핑 테이블도 함께 둡니다.

```json
// careermate/data/role_skill_map.json
{
  "백엔드 개발자": ["Python", "FastAPI", "SQL", "Docker", "Git"],
  "프론트엔드 개발자": ["JavaScript", "React", "CSS", "Git"],
  "데이터 분석가": ["Python", "SQL", "Pandas", "시각화(Matplotlib)"]
}
```

#### 2-2. 툴 함수 구현

```python
# careermate/tools.py
import json, pathlib, re
from .state import SkillRecord, ResourceItem

_DB_PATH   = pathlib.Path(__file__).parent / "data" / "skill_db.json"
_ROLE_PATH = pathlib.Path(__file__).parent / "data" / "role_skill_map.json"
_ALIAS: dict[str, str] = {          # 별칭 테이블 (normalize_skill_name 용)
    "react.js": "React",
    "reactjs":  "React",
    "fastapi":  "FastAPI",
    "py":       "Python",
}

_DB:   dict = json.loads(_DB_PATH.read_text())
_ROLE: dict = json.loads(_ROLE_PATH.read_text())

def normalize_skill_name(raw: str) -> str:
    """자유 표기 → 사전 키 정규화. 실패 시 raw 반환(throw 금지)."""
    key = raw.strip().lower()
    return _ALIAS.get(key, raw)

def lookup_skill(name: str) -> SkillRecord:
    """
    스킬 사전 조회. 미존재 시 status='unknown', verified=False 반환.
    예외/IO 오류도 unknown 폴백(throw 금지).
    """
    canonical = normalize_skill_name(name)
    entry = _DB.get(canonical)
    if entry is None:
        return SkillRecord(
            name=canonical, status="unknown",
            prereqs=[], resources=[], typical_hours=0, verified=False,
        )
    return SkillRecord(
        name=canonical, status="known",
        prereqs=entry["prereqs"],
        resources=[ResourceItem(**r) for r in entry["resources"]],
        typical_hours=entry["typical_hours"],
        verified=True,
    )

def list_skills_for_role(role: str) -> list[SkillRecord]:
    """직무 → 관련 스킬 일괄 조회. 미매핑 시 빈 리스트(throw 금지)."""
    names = _ROLE.get(role, [])
    return [lookup_skill(n) for n in names]
```

**Day 3 확인 체크포인트:**
- `lookup_skill("Python")` → `status="known"`, `verified=True`, prereqs=[]
- `lookup_skill("없는스킬")` → `status="unknown"`, `verified=False`
- `normalize_skill_name("react.js")` → `"React"`
- `list_skills_for_role("백엔드 개발자")` → 5개 SkillRecord 리스트

> **Claude Code 팁:** 툴 함수를 먼저 작성하고 대화형으로 `lookup_skill("FastAPI")` 출력을 확인한 뒤 다음 노드 구현으로 넘어가세요. 사전에 없는 스킬을 넣었을 때 예외 없이 unknown을 반환하는지 꼭 확인하세요.

---

### M3 (Day 4-5): 모호성 라우터 + clarify 노드

**목표:** 자율 라우팅 달성. 온보딩 직후 ambiguity_score로 ask/proceed 분기.

이것이 피드백 제안 1번이자 "가장 효율 높은 작업"입니다 (feedback.md 7페이지 해설).
LangGraph conditional edge 하나로 '고정 직선'을 '상황 인지 분기'로 바꿉니다.

#### 3-1. TriageRouter 노드

```python
# careermate/nodes/triage_router.py
from ..state import AgentState, TraceEntry
from ..llm import call_llm   # 팀 내 LLM 호출 헬퍼
import json, datetime

AMBIGUITY_THRESHOLD = 0.6    # 이 값 초과 시 ask 분기

_TRIAGE_PROMPT = """\
아래 온보딩 입력을 보고 JSON으로만 답하세요.
- ambiguity_score: float (0.0~1.0). 목표직무가 막연하거나 정보가 부족할수록 높음.
- reasons: list[str]. 모호도가 높은 근거 (없으면 빈 리스트).

온보딩 입력:
{onboarding_json}

반환 형식: {{"ambiguity_score": 0.0, "reasons": []}}
"""

def triage_router_node(state: AgentState) -> dict:
    prompt = _TRIAGE_PROMPT.format(
        onboarding_json=state.onboarding_input.model_dump_json(indent=2)
    )
    raw = call_llm(prompt)
    parsed = json.loads(raw)
    score = float(parsed.get("ambiguity_score", 0.5))
    decision = "ask" if score > AMBIGUITY_THRESHOLD else "proceed"

    entry = TraceEntry(
        node="triage_router",
        input_summary=f"target_role={state.onboarding_input.target_role}",
        decision=decision,
        tool_called=None,
        output_summary=f"ambiguity_score={score:.2f} → {decision}",
        ts=datetime.datetime.utcnow().isoformat(),
    )
    return {
        "ambiguity_score": score,
        "route_decision":  decision,
        "trace": [entry],
    }
```

#### 3-2. Clarify 노드

```python
# careermate/nodes/clarify.py
_CLARIFY_PROMPT = """\
사용자의 온보딩 입력이 모호합니다. 아래 중 하나를 수행하세요.
A) 목표 직무가 불분명하면: 유사 직무 2~3개 후보를 제시하고 선택을 요청하세요.
B) 정보가 부족하면: 역질문 2~3개를 리스트로 제시하세요.

온보딩 입력: {onboarding_json}
모호 근거:   {reasons}

반환 형식 (JSON):
{{
  "kind": "similar_role_pick" | "info_supplement",
  "question": "사용자에게 보여줄 질문/선택지 텍스트"
}}
"""

def clarify_node(state: AgentState) -> dict:
    # 실제 구현에서는 프론트엔드로 질문을 보내고
    # 사용자 응답을 받아 clarify_answers에 추가합니다.
    # MVP에서는 interrupt() 또는 human-in-the-loop 패턴 사용.
    ...
    entry = TraceEntry(
        node="clarify",
        input_summary="ask 경로 진입",
        decision=None,
        tool_called=None,
        output_summary="역질문 전송 완료",
        ts=datetime.datetime.utcnow().isoformat(),
    )
    return {"trace": [entry]}
```

> **LangGraph human-in-the-loop:** clarify 노드에서 사용자 응답을 기다리려면 `interrupt()` 함수를 사용합니다.
> ```python
> from langgraph.types import interrupt
> answer = interrupt({"question": question_text})   # 여기서 그래프 일시 중단
> ```
> 재개 시 `graph.invoke(Command(resume=user_answer), config={"thread_id": ...})`로 답변을 주입합니다.

**Day 5 확인 체크포인트:**
- 목표직무="IT 관련 일"로 입력 → ambiguity_score > 0.6, route_decision="ask"
- 목표직무="백엔드 개발자"로 입력 → route_decision="proceed"
- clarify → triage_router 복귀 엣지가 그래프에서 실행됨
- trace에 triage_router 항목이 정상 append됨

---

### M4 (Day 6-7): 핵심 에이전트 노드 (Profile / Job / Gap)

**목표:** 세 에이전트 노드 구현 + Gap→Job 되먹임 엣지 동작.

#### 4-1. ProfileDiagnosisAgent 노드 (요약)

```python
# careermate/nodes/profile_diagnosis.py
_PROFILE_PROMPT = """\
아래 온보딩 입력만을 근거로 역량을 진단하세요.
입력 외 정보를 추론·추가하지 마세요 (입력 외 추론 금지).

온보딩 입력: {onboarding_json}
보완 응답:   {clarify_json}
직전 진행기록: {episodic_json}

반환 형식 (JSON):
{{
  "summary":        "string",
  "strengths":      ["string"],
  "weaknesses":     ["string"],
  "interests":      ["string"],
  "readiness_level": "low|mid|high"
}}
"""

def profile_diagnosis_node(state: AgentState) -> dict:
    # 직전 기억에서 완료 주차 스킬은 weaknesses 후보에서 제외
    episodic_ctx = _extract_completed_skills(state.episodic_memory)
    ...
```

#### 4-2. JobRequirementAgent 노드 (요약)

```python
_JOB_PROMPT = """\
목표 직무/공고 텍스트에서 역량을 추출하세요.
홍보성 문구('글로벌 리더', '열정 있는 인재' 등)는 제거하세요.
evidence_strength: 공고 텍스트가 충분하면 "strong", 너무 짧거나 없으면 "weak".

목표 직무: {target_role}
공고 텍스트: {job_posting_text}
재요청 사유: {rerun_reason}   ← rerun 시에만 채워짐

반환 형식 (JSON): JobRequirement 스키마
"""
```

#### 4-3. GapAnalysis 노드 (lookup_skill 툴 사용)

```python
# careermate/nodes/gap_analysis.py
from ..tools import lookup_skill, normalize_skill_name

def gap_analysis_node(state: AgentState) -> dict:
    profile  = state.profile
    job_req  = state.job_requirement
    gaps: list[GapItem] = []
    all_verified = True

    for raw_skill in job_req.required_skills:
        canonical = normalize_skill_name(raw_skill)
        if canonical in profile.strengths:
            continue                          # 보유 → 갭 아님

        record = lookup_skill(canonical)      # ← tool use (ReAct 패턴)
        if not record.verified:
            all_verified = False              # unknown → State.verified 내림

        gaps.append(GapItem(
            skill=canonical,
            priority=_calc_priority(canonical, job_req),
            current_level="없음",
            target_level="기본 이상",
            skill_status=record.status,
            verified=record.verified,
        ))

    needs_rerun = (
        job_req.evidence_strength == "weak"
        and state.rerun_count < MAX_RERUN
    )
    entry = TraceEntry(
        node="gap_analysis",
        input_summary=f"gaps={len(gaps)}, evidence={job_req.evidence_strength}",
        decision="rerun_job" if needs_rerun else "skip_rerun",
        tool_called="lookup_skill",
        output_summary=f"needs_rerun={needs_rerun}",
        ts=_now(),
    )
    return {
        "gap_analysis":  GapAnalysis(gaps=gaps, ...),
        "needs_rerun":   needs_rerun,
        "rerun_reason":  "공고 근거 약함, 재추출 요청" if needs_rerun else None,
        # rerun_count는 _gap_router(conditional edge)에서만 증가 — 노드 본문 증가 금지
        "verified":      all_verified,
        "trace":         [entry],
    }
```

**Day 7 확인 체크포인트:**
- 정상 공고 입력 → evidence_strength="strong", needs_rerun=False → roadmap_plan 진행
- 짧은 공고 입력 → evidence_strength="weak", needs_rerun=True → job_requirement 재실행(1회)
- rerun_count=1 이후 재차 weak → needs_rerun=False, roadmap_plan으로 진행(무한루프 방지)
- gap_analysis.gaps에 known/unknown 스킬 혼재 시 State.verified=False

---

### M5 (Day 8-9): roadmap_plan + roadmap_critic 루프

**목표:** reflection + guardrails 동시 달성. Critic이 4종 체크리스트로 로드맵을 검증하고 위반 시 재생성.

이것이 피드백 제안 3번(Critic 루프)이며 "가장 에이전트다운" 증거가 됩니다 (Reflexion, Self-Refine).

#### 5-1. roadmap_plan 노드

```python
# careermate/nodes/roadmap_plan.py
_PLAN_PROMPT = """\
아래 갭 분석과 스킬 정보로 주차별 로드맵을 생성하세요.

[Plan-and-Solve 접근]
1. 먼저 총 학습 시간을 산출: sum(gap_skills의 typical_hours)
2. 주당 가용 시간: {weekly_hours}h
3. 필요 주차 = ceil(총 시간 / weekly_hours) → roadmap_horizon 결정
4. 주차별로 covered_skills, planned_hours (≤ weekly_hours), 과제를 배치

갭 분석:       {gap_json}
스킬 상세:     {skill_records_json}
이전 Critic 위반 (재생성 시): {violations_json}
이전 진행기록: {episodic_json}

반환 형식 (JSON): Roadmap 스키마
금칙 표현: '합격 가능', '반드시 합격', '취업 보장', '진로 확정' — 절대 포함 금지
"""

def roadmap_plan_node(state: AgentState) -> dict:
    # lookup_skill로 각 gap 스킬의 선후행·자원·시간 수집
    skill_records = {
        gap.skill: lookup_skill(gap.skill)
        for gap in state.gap_analysis.gaps
    }
    # 선후행 순서로 갭 정렬 (prereq_order_violation 방지)
    ordered_gaps = _topological_sort(state.gap_analysis.gaps, skill_records)

    violations_ctx = (
        state.critic_report.violations
        if state.critic_report else []
    )
    ...
    entry = TraceEntry(
        node="roadmap_plan",
        input_summary=f"revision={state.revision_count}, gaps={len(ordered_gaps)}",
        decision=None,
        tool_called="lookup_skill",
        output_summary=f"horizon={roadmap.horizon}, weeks={roadmap.total_weeks}",
        ts=_now(),
    )
    return {
        "roadmap":        roadmap,
        # revision_count는 _critic_router(conditional edge)에서만 증가 — 노드 본문 증가 금지
        "trace":          [entry],
    }
```

#### 5-2. roadmap_critic 노드 (핵심: reflection + guardrails)

```python
# careermate/nodes/roadmap_critic.py
FORBIDDEN_PHRASES = ["합격 가능", "반드시 합격", "취업 보장", "진로 확정", "100% 합격"]

def roadmap_critic_node(state: AgentState) -> dict:
    """
    4종 체크리스트 검증 (Reflexion / Self-Refine 패턴).
    위반 시 verdict="revise", roadmap_plan 루프백.
    """
    roadmap = state.roadmap
    gaps    = state.gap_analysis.gaps
    violations: list[Violation] = []

    # [검증 1] 부족역량 커버율: 모든 high/medium gap이 roadmap에 1회 이상 매핑
    covered = {skill for w in roadmap.weeks for skill in w.covered_skills}
    for gap in gaps:
        if gap.priority in ("high", "medium") and gap.skill not in covered:
            violations.append(Violation(
                type="uncovered_gap",
                detail=f"{gap.skill}(priority={gap.priority})이 로드맵에 없음",
                location="roadmap 전체",
            ))

    # [검증 2] 주차별 시간 예산: planned_hours <= weekly_hours_budget
    for week in roadmap.weeks:
        if week.planned_hours > roadmap.weekly_hours_budget:
            violations.append(Violation(
                type="time_budget_exceeded",
                detail=f"{week.planned_hours}h > 가용 {roadmap.weekly_hours_budget}h",
                location=f"week {week.week_index}",
            ))

    # [검증 3] 선후행 위반: prereq가 더 늦은 주차에 배치되면 위반
    skill_week: dict[str, int] = {}
    for week in roadmap.weeks:
        for skill in week.covered_skills:
            skill_week[skill] = week.week_index
    for week in roadmap.weeks:
        for skill in week.covered_skills:
            record = lookup_skill(skill)
            for prereq in record.prereqs:
                if prereq in skill_week and skill_week[prereq] > week.week_index:
                    violations.append(Violation(
                        type="prereq_order_violation",
                        detail=f"{prereq}(선행)가 {skill}(후행)보다 늦게 배치됨",
                        location=f"week {week.week_index}",
                    ))

    # [검증 4] 금칙 표현 스캔
    all_text = roadmap.model_dump_json()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in all_text:
            violations.append(Violation(
                type="forbidden_phrase",
                detail=f'금칙 표현 "{phrase}" 발견',
                location="roadmap 전체",
            ))

    verdict = "pass" if not violations else "revise"
    report  = CriticReport(
        verdict=verdict,
        violations=violations,
        checked_at_revision=state.revision_count,
    )
    entry = TraceEntry(
        node="roadmap_critic",
        input_summary=f"revision={state.revision_count}",
        decision=verdict,
        tool_called="lookup_skill",   # 선후행 검증에서 사용
        output_summary=f"verdict={verdict}, violations={len(violations)}",
        ts=_now(),
    )
    return {"critic_report": report, "trace": [entry]}
```

**Day 9 확인 체크포인트:**
- 정상 로드맵 → violations=[], verdict="pass" → finalize
- weekly_hours 초과 주차 삽입 → time_budget_exceeded 위반 → revise → roadmap_plan 재실행
- revision_count=2 도달 시 위반 남아도 "pass"로 강제 finalize (_critic_router 조건)
- "합격 보장" 문구 삽입 → forbidden_phrase 위반 → revise

---

### M6 (Day 10): episodic 메모리 + trace + 통합 테스트

**목표:** 재방문 사용자 흐름 동작 + 전체 그래프 end-to-end 통과.

#### 6-1. progress_reconciliation 노드

```python
# careermate/nodes/progress_reconciliation.py
def progress_reconciliation_node(state: AgentState) -> dict:
    mem = state.episodic_memory
    if mem is None or mem.status == "new_user":
        entry = TraceEntry(node="progress_reconciliation",
                           input_summary="신규 사용자",
                           decision="skip_reconcile", ...)
        return {"trace": [entry]}

    # 완료 주차의 covered_skills → 이미 보유로 간주 (weaknesses에서 제외)
    completed_skills: list[str] = []
    incomplete_skills: list[str] = []
    for wp in mem.weekly_progress:
        week_plan = _find_week(mem.last_roadmap, wp.week_index)
        if week_plan:
            if wp.completed:
                completed_skills.extend(week_plan.covered_skills)
            else:
                incomplete_skills.extend(week_plan.covered_skills)

    # 이월 정보를 state 확장 필드 또는 onboarding_input.concern에 주입
    # (MVP: concern 필드에 텍스트로 덧붙이는 방식)
    carry_over_note = (
        f"[이전 로드맵 이월] 미완료 스킬: {', '.join(incomplete_skills)}. "
        f"완료 스킬(보유로 간주): {', '.join(completed_skills)}."
    ) if incomplete_skills or completed_skills else ""

    entry = TraceEntry(node="progress_reconciliation",
                       input_summary=f"returning_user, 미완료={len(incomplete_skills)}",
                       decision="reconcile", ...)
    return {"trace": [entry], "_carry_over_note": carry_over_note}
```

#### 6-2. finalize 노드

```python
def finalize_node(state: AgentState) -> dict:
    disclaimer = (
        "이 로드맵은 커리어 준비를 돕기 위한 참고 자료입니다. "
        "합격 가능성이나 진로를 단정하지 않으며, "
        "검증 안 됨 항목은 추가 확인을 권장합니다."
    )
    output = FinalOutput(
        profile=state.profile,
        gap_analysis=state.gap_analysis,
        roadmap=state.roadmap,
        verified=state.verified,
        trace_summary=state.trace,
        disclaimer=disclaimer,
    )
    return {"final_output": output}
```

#### 6-3. 통합 테스트 시나리오 (3가지)

| # | 시나리오 | 확인 포인트 |
|---|----------|-------------|
| T1 | 신규 사용자, 명확한 직무(백엔드 개발자), 정상 공고 | route=proceed, rerun=없음, critic=pass(1~2회 이내), trace 6+ 항목 |
| T2 | 신규 사용자, 모호한 직무("IT 관련") | route=ask → clarify → proceed 수렴, trace에 ask 결정 기록 |
| T3 | 재방문 사용자, 직전 로드맵 2주 완료 | reconcile 결정, 완료 스킬 제외, 미완료 이월 반영된 로드맵 |

---

## 2. 절대 하지 말 것

> 이 항목을 어기면 1.5주 일정이 폭주합니다 (feedback.md 1.5주 조언).

| 금지 항목 | 이유 |
|-----------|------|
| 대규모 사이트 크롤링(채용 사이트 봇 순회·HTML 대량 수집) | MVP 범위 외. 검색 API(web_search)는 허용 — 검색 엔진이 색인한 결과 메타데이터(title·url·snippet)만 수신하며, 대상 사이트 HTML을 직접 파싱·순회하지 않음. 단일 페이지 직접 fetch/HTML 파싱도 1.5주 범위에서는 금지 |
| 파인튜닝·데이터 수집 | 일정·인프라 모두 초과. 프롬프트 엔지니어링으로 충분 |
| 멀티 직무 일반화 | 스킬 DB를 IT 직무 1~2개로 작게 유지해야 1.5주 내 완성 가능 |
| 프론트엔드 완성도에 시간 투자 | 에이전트 그래프·툴·검증 로직 먼저. UI는 stub JSON 출력으로 대체 |
| 로드맵 기간 고정(4/8주 선택지) | Plan-and-Solve로 갭 크기·가용시간에서 기간을 산출하는 것이 핵심 |

---

## 3. Claude Code 활용 팁

### 노드별 작은 테스트 먼저

각 노드를 완성할 때마다 그래프 전체 실행 전에 단위로 호출하세요.

```python
# 노드 단위 테스트 패턴
from careermate.state import AgentState
from careermate.nodes.triage_router import triage_router_node

state = AgentState(
    user_id="test-001", session_id="s1",
    onboarding_input=OnboardingInput(
        major="컴퓨터공학", current_status="재학", interests=["웹개발"],
        owned_skills=["Python 기초"], target_role="백엔드 개발자",
        weekly_hours=10, concern=None, job_posting_text=None,
    ),
)
result = triage_router_node(state)
print(result["route_decision"])  # "proceed" 기대
print(result["trace"][0].decision)
```

### 스킬 DB 먼저 작성

스킬 DB JSON을 먼저 완성하면 이후 모든 노드 테스트에서 실제 데이터를 쓸 수 있습니다.
Claude Code에 "백엔드 개발자 스킬 50개, 선후행 포함 JSON 작성해줘"를 요청하면 초안이 빠르게 나옵니다.
이후 verified=true 자원만 수작업으로 검수하세요 (링크가 실재하는지 확인).

### 조건 엣지 디버깅

LangGraph 그래프에서 조건 엣지가 의도대로 작동하는지 확인하려면:

```python
# 그래프 실행 시 각 노드의 입출력을 스트리밍으로 확인
for event in graph.stream(initial_state):
    for node_name, output in event.items():
        print(f"[{node_name}] trace: {output.get('trace', [])}")
```

### Critic 루프 단독 테스트

```python
# 의도적 위반을 포함한 로드맵으로 critic만 단독 테스트
bad_roadmap = Roadmap(
    horizon="weeks_4", total_weeks=4,
    weekly_hours_budget=10,
    weeks=[WeekPlan(week_index=1, objectives=[], tasks=[],
                    covered_skills=[], planned_hours=20)],  # ← 예산 초과
    rationale="테스트용",
)
state.roadmap = bad_roadmap
result = roadmap_critic_node(state)
assert result["critic_report"].verdict == "revise"
assert any(v.type == "time_budget_exceeded" for v in result["critic_report"].violations)
```

---

## 4. 산출물 체크리스트

발표 전 아래를 모두 체크하세요.

### 에이전트 구조 (필수)
- [ ] LangGraph `StateGraph` 빌드 성공 (에러 없음)
- [ ] `AgentState` Pydantic 모델에 설계 스키마 전체 필드 반영
- [ ] conditional edge 3개 동작: triage / gap→job / critic
- [ ] trace 리스트에 전체 노드 실행 기록 누적

### 3대 개선 (필수)
- [ ] **모호성 라우터:** ambiguity_score 산정 → ask/proceed 분기 → trace에 결정 기록
- [ ] **스킬 DB:** skill_db.json 50행 이상, lookup_skill("Python") known 반환
- [ ] **Critic 루프:** 4종 체크리스트 동작, revise 시 roadmap_plan 루프백, MAX_REVISIONS=2 가드

### 에이전트 협업 (필수)
- [ ] Gap→Job 되먹임: evidence_strength="weak" → needs_rerun=True → job_requirement 재실행(1회)
- [ ] verified 플래그: unknown 스킬 포함 시 State.verified=False, disclaimer 포함

### 메모리
- [ ] episodic_memory=None(신규) 시 오류 없이 통과
- [ ] returning_user 시 progress_reconciliation 동작, trace에 reconcile 기록

### 통합
- [ ] T1/T2/T3 시나리오 end-to-end 실행 성공
- [ ] final_output.disclaimer 항상 포함

---

## 5. 위험 요소와 컷오버 기준

| 위험 요소 | 가능성 | 대응 |
|-----------|--------|------|
| clarify 노드 human-in-the-loop 구현 복잡 | 중 | MVP: interrupt() 대신 ask 분기 시 로그만 남기고 proceed로 자동 진행(데모용). LangGraph interrupt 공식 문서 먼저 확인 |
| LLM 출력이 JSON 파싱 실패 | 중 | try/except + json.loads 실패 시 기본값 반환. 필드 누락은 Pydantic `model_validate` 로 잡음 |
| 스킬 DB에 없는 직무 입력 | 높음 | list_skills_for_role 빈 리스트 반환 → job_requirement 기반으로 폴백. verified=False 표기 |
| Critic 루프 무한 반복 | 낮음 | MAX_REVISIONS=2 가드. _critic_router에서 revision_count >= MAX_REVISIONS → "pass" 강제 |
| 재방문 사용자 DB 스키마 없음 | 중 | MVP: JSON 파일로 대체(`user_memory/{user_id}.json`). DB는 발표 후 연결 |

### 컷오버 기준

일정이 밀리면 아래 순서로 범위를 줄이세요:

1. **반드시 유지:** 그래프 골격 + 상태 스키마 + 3대 개선(라우터/Critic/스킬DB)
2. **중간 삭제 가능:** clarify human-in-the-loop (로그 출력으로 대체)
3. **마지막 삭제 가능:** episodic 메모리 (신규 사용자만 지원, returning_user 분기 skip)
4. **절대 삭제 불가:** trace 로그 (발표에서 에이전시 증거로 가장 중요)

---

## 6. 연관 문서

- [에이전트 그래프 설계](02-agent-graph.md) — 노드·엣지·상태 스키마 전체
- [툴·스킬 DB 명세](04-tools-skill-db.md) — skill_db.json 전체 + lookup_skill + web_search 계약
- [Pydantic 데이터 모델](06-data-model.md) — 모든 모델 필드 명세 (ResourceItem·SearchHit 포함)
- [트레이스·메모리 설계](06-data-model.md) — TraceEntry, EpisodicMemory 상세

---

## 참고 문헌

| 자료 | 이 플랜에서 적용된 곳 |
|------|----------------------|
| Anthropic, *Building Effective Agents* (2024) | workflow vs agent 구분, 라우터·evaluator 패턴 → M3 triage_router, M5 Critic |
| Yao et al., *ReAct* (2022) | Thought+Act 교대, 도구 호출로 환각 억제 → M2 lookup_skill, M4 gap_analysis |
| Shinn et al., *Reflexion* (2023) | 자기 비판 → 재시도 루프 → M5 roadmap_critic + revise 엣지 |
| Madaan et al., *Self-Refine* (2023) | 단일 모델 자기 피드백 개선 → M5 Critic 체크리스트 구조 |
| Wang et al., *Plan-and-Solve Prompting* (2023) | 하위 과제 분해 후 단계 실행 → M5 roadmap_plan 기간 산출 로직 |
| LangGraph Docs, *Conditional Edges & State* | 조건 엣지·상태 병합 구현 → M1 그래프 골격, 모든 conditional_edge |
