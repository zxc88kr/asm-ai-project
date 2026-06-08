# 평가 & KPI (에이전트 관점)

이 문서는 CareerMate의 원본 8페이지 KPI를 "에이전트가 스스로 측정·검증할 수 있는 지표"로 재정의하고, 평가 방법·평가셋·데모 시나리오를 구체적으로 기술합니다. "측정 불가능한 허수 지표"를 없애고, Critic/reflection 노드([에이전트 그래프](02-agent-graph.md) 참조)가 자동 산출하는 수치로 대체합니다.

---

## 1. 원본 KPI의 문제와 재정의 방향

### 원본 KPI (8페이지 발췌)

| 원본 항목 | 문제점 |
|-----------|--------|
| 로드맵 구체성 평가 | "구체적"의 기준이 없음 → 평가자마다 결과가 달라짐 |
| 로드맵 생성 성공률 | 오류 없이 JSON이 반환되면 100% → 내용 품질과 무관 |
| 사용자 만족도 | 설문 주관성 높음, 자동 측정 불가, 1.5주 내 표본 부족 |

### 재정의 원칙

- **자동 측정 가능(Automatable):** Critic 노드나 테스트 코드가 직접 계산.
- **에이전트 행동 증명(Agency Evidence):** 라우팅·툴 호출·reflection이 실제로 발생했음을 수치로.
- **임계값 명시(Threshold-defined):** "몇 %이면 합격"을 사전에 정의.

---

## 2. 핵심 KPI 정의

### KPI 1. 부족역량 커버율 (Gap Coverage Rate)

**정의:** 로드맵이 `GapAnalysis.gaps` 리스트의 모든 스킬을 1개 이상의 주차에 배치했는지 비율.

**한 줄 풀이:** "발견된 부족 역량이 로드맵에 빠짐없이 들어갔는가?"

```python
def gap_coverage_rate(gap_analysis: GapAnalysis, roadmap: Roadmap) -> float:
    """
    반환: 0.0 ~ 1.0
    Critic 노드의 uncovered_gap 체크와 같은 로직.
    """
    required = {g.skill for g in gap_analysis.gaps}
    covered = set()
    for week in roadmap.weeks:
        covered.update(week.covered_skills)
    if not required:
        return 1.0
    return len(required & covered) / len(required)
```

| 임계값 | 의미 |
|--------|------|
| `< 1.0` | Critic이 `uncovered_gap` 위반 발급 → `revise` 판정 (Reflexion 루프 발동) |
| `== 1.0` | 커버 완료 → 이 항목 통과 |

**목표:** 최종 `FinalOutput` 기준 **100%** (Critic이 보장).

---

### KPI 2. 시간예산 위반 건수 (Time Budget Violations)

**정의:** `WeekPlan.planned_hours > OnboardingInput.weekly_hours` 인 주차 수.

**한 줄 풀이:** "사용자가 낼 수 있는 시간보다 많이 배정된 주가 몇 개인가?"

```python
def time_budget_violations(roadmap: Roadmap) -> list[dict]:
    """
    반환: 위반 주차 리스트. 최종 출력 기준 0이어야 함.
    """
    budget = roadmap.weekly_hours_budget
    violations = []
    for week in roadmap.weeks:
        if week.planned_hours > budget:
            violations.append({
                "week_index": week.week_index,
                "planned_hours": week.planned_hours,
                "budget": budget,
                "excess": week.planned_hours - budget,
            })
    return violations
```

**목표:** 최종 `FinalOutput` 기준 **위반 0건** (Critic `time_budget_exceeded` 체크가 보장).

---

### KPI 3. 선후행 위반 건수 (Prerequisite Order Violations)

**정의:** `SkillRecord.prereqs` 기준, 선행 스킬보다 후행 스킬이 앞 주차에 배치된 경우 수.

**한 줄 풀이:** "파이썬을 배우기 전에 머신러닝을 먼저 넣은 주차가 있는가?"

```python
def prereq_order_violations(roadmap: Roadmap, skill_db: dict[str, SkillRecord]) -> list[dict]:
    """
    반환: 위반 항목 리스트. 최종 출력 기준 0이어야 함.
    lookup_skill로 얻은 prereqs 기반 검사.
    """
    skill_week: dict[str, int] = {}
    for week in roadmap.weeks:
        for skill in week.covered_skills:
            skill_week[skill] = week.week_index

    violations = []
    for skill, week_idx in skill_week.items():
        record = skill_db.get(skill)
        if not record:
            continue
        for prereq in record.prereqs:
            prereq_week = skill_week.get(prereq)
            if prereq_week is not None and prereq_week > week_idx:
                violations.append({
                    "skill": skill,
                    "prereq": prereq,
                    "skill_week": week_idx,
                    "prereq_week": prereq_week,
                })
    return violations
```

**목표:** 최종 `FinalOutput` 기준 **위반 0건** (Critic `prereq_order_violation` 체크가 보장).

---

### KPI 4. 라우터 ask/proceed 정확도 (Router Accuracy)

**정의:** 평가셋 입력에 대해 `TriageRouter`가 정답 레이블(`ask` 또는 `proceed`)을 맞힌 비율.

**한 줄 풀이:** "모호한 입력은 되묻고, 충분한 입력은 바로 진행하는가?"

```python
# 평가 실행 예시
def evaluate_router(test_cases: list[RouterTestCase]) -> float:
    """
    RouterTestCase = {
        "input": OnboardingInput,
        "expected_decision": "ask" | "proceed"
    }
    """
    correct = sum(
        1 for tc in test_cases
        if run_triage_router(tc["input"]).route_decision == tc["expected_decision"]
    )
    return correct / len(test_cases)
```

**목표:** **≥ 80%** (평가셋 10케이스 기준 8/10 이상).

---

### KPI 5. 스킬 DB Hit율 및 웹검색 보강율 (Tool Hit Rate & Web Search Coverage)

**정의:** `lookup_skill` 호출 중 `status == "known"` 반환 비율(DB Hit율)과, unknown 스킬 중 `web_search`로 실제 url을 확보한 비율(웹 보강율), 검색 실패 시 llm 폴백율.

**한 줄 풀이:** "로드맵에 들어간 스킬이 DB(캐시) 또는 웹검색으로 검증됐는가? 순수 LLM 자체지식(환각 위험)에 의존한 비율은 얼마인가?"

```python
def tool_hit_rate(trace: list[TraceEntry]) -> float:
    """
    trace에서 tool_called == 'lookup_skill' 인 항목 기준.
    실제 known/unknown은 GapItem.skill_status로 집계.
    """
    lookup_calls = [e for e in trace if e.tool_called == "lookup_skill"]
    if not lookup_calls:
        return 0.0
    # GapItem.verified == True 개수 / 전체 GapItem 수로 근사
    # (TraceEntry에서 직접 집계하려면 output_summary 파싱 필요)
    return ...  # 호출자가 GapAnalysis.gaps 기준으로 계산
```

실용적 집계 (DB Hit율 + 웹 보강율 분해):

```python
def tool_hit_rate_from_gap(gap_analysis: GapAnalysis) -> dict:
    """
    반환 예시:
    {
      "db_hit_rate":  0.65,   # lookup_skill known / 전체 갭 스킬
      "web_aug_rate": 0.25,   # unknown이지만 web_search로 url 확보 / 전체 갭 스킬
      "llm_fallback_rate": 0.10,  # 검색까지 실패해 llm origin(verified=False) / 전체 갭 스킬
    }
    검증된 비율 = db_hit_rate + web_aug_rate (origin=db 또는 web, verified=True)
    미검증 폴백율 = llm_fallback_rate (origin=llm, verified=False)
    """
    items = gap_analysis.gaps
    if not items:
        return {"db_hit_rate": 1.0, "web_aug_rate": 0.0, "llm_fallback_rate": 0.0}
    n = len(items)
    db_known  = sum(1 for g in items if g.skill_status == "known")
    web_aug   = sum(1 for g in items if g.skill_status == "unknown" and g.origin == "web")
    llm_fall  = sum(1 for g in items if g.origin == "llm")
    return {
        "db_hit_rate":      db_known / n,
        "web_aug_rate":     web_aug / n,
        "llm_fallback_rate": llm_fall / n,
    }
```

**검색 결과 활용률 (근거 url 포함 비율):**

```python
def search_url_coverage(roadmap: Roadmap) -> float:
    """
    roadmap.weeks 전체 TaskItem.resources 중 url이 실제로 존재하는(None이 아닌) 비율.
    web_search 도입 전후 비교 지표 — 도입 후 url 보유 비율이 증가해야 함.
    """
    all_resources = [
        r for week in roadmap.weeks
        for task in week.tasks
        for r in task.resources
    ]
    if not all_resources:
        return 1.0
    with_url = sum(1 for r in all_resources if r.url is not None)
    return with_url / len(all_resources)
```

**검색 실패 시 폴백 동작 (search_degraded 추적):**

```python
def search_degraded_summary(state: CareerMateState) -> dict:
    """
    검색 폴백 발생 여부와 실제 검색 호출 횟수를 집계.
    search_degraded=True이면 disclaimer에 '일부 자원은 웹검색 출처 미확보' 고지 필요.
    """
    return {
        "search_count":    state.get("search_count", 0),
        "search_degraded": state.get("search_degraded", False),
        # degraded=True 시 llm_fallback_rate가 높아지므로 함께 보고
    }
```

> **폴백 정책:** `search_degraded=True`(API 오류·타임아웃·`MAX_SEARCH=8` 초과)이면 해당 스킬 리소스를 `origin="llm"`, `verified=False`로 표기하고 `FinalOutput` disclaimer에 반영합니다. 검색 실패가 로드맵 전체 품질을 막지는 않으며, llm_fallback_rate가 ≤ 20%이면 허용 범위로 봅니다.

**목표:**
- DB Hit율 **≥ 70%** (IT 직무 2개, 50~150행 사전 기준)
- 검증된 비율(db + web) **≥ 80%** (1.5주 범위 선택사항 목표)
- 미검증 폴백율(llm) **≤ 20%**

---

### KPI 6. Critic 재생성 횟수 분포 (Revision Count Distribution)

**정의:** 평가셋 전체에서 `revision_count` 값의 분포(0회·1회·2회 각 비율).

**한 줄 풀이:** "로드맵을 처음부터 잘 만들수록 재생성이 적다 — reflection이 실제로 발동됐음을 증명하는 지표."

| revision_count | 의미 | 기대 비율 |
|---------------|------|-----------|
| 0 | 첫 생성 통과 | ≥ 50% |
| 1 | 1회 재생성 후 통과 | ≥ 30% |
| 2 (MAX_REVISIONS) | 강제 finalize | ≤ 20% |

집계:

```python
from collections import Counter

def revision_distribution(results: list[dict]) -> dict:
    """results: [{"revision_count": int, ...}, ...]"""
    c = Counter(r["revision_count"] for r in results)
    total = len(results)
    return {k: round(v / total, 2) for k, v in sorted(c.items())}
```

---

## 3. KPI 전체 요약표

| # | KPI | 측정 방법 | 목표값 | 자동화 주체 |
|---|-----|-----------|--------|------------|
| 1 | 부족역량 커버율 | `gap_coverage_rate()` | **100%** | `roadmap_critic` 노드 |
| 2 | 시간예산 위반 건수 | `time_budget_violations()` | **0건** | `roadmap_critic` 노드 |
| 3 | 선후행 위반 건수 | `prereq_order_violations()` | **0건** | `roadmap_critic` 노드 |
| 4 | 라우터 정확도 | `evaluate_router()` | **≥ 80%** | 오프라인 평가 스크립트 |
| 5 | 스킬 DB Hit율 | `tool_hit_rate_from_gap()` | **≥ 70%** | `gap_analysis` State 집계 |
| 5-a | 웹 보강율(검색 결과 활용률) | `tool_hit_rate_from_gap()["web_aug_rate"]` | (db+web) **≥ 80%** *(선택사항)* | `gap_analysis`/`roadmap_plan` State |
| 5-b | 근거 url 포함 비율 | `search_url_coverage()` | url 있는 리소스 **≥ 80%** *(선택사항)* | `roadmap_plan` 출력 집계 |
| 5-c | 미검증 폴백율 (llm origin) | `tool_hit_rate_from_gap()["llm_fallback_rate"]` | **≤ 20%** *(선택사항)* | State `search_degraded` 추적 |
| 6 | Critic 재생성 분포 | `revision_distribution()` | 0회 ≥ 50% | 로그 후처리 스크립트 |

> KPI 1·2·3은 `roadmap_critic` 노드가 매 실행 시 자동 검증합니다 (Reflexion, Shinn et al. 2023). KPI 4·5·6은 평가 스크립트로 배치 측정합니다. KPI 5-a·5-b·5-c는 웹검색 도입 후 선택적으로 추적하는 보조 지표이며 1.5주 범위 내 필수 목표는 아닙니다 (과설계 금지).

---

## 4. 평가셋 구성

### 4.1 샘플 사용자 10케이스

평가셋은 다음 두 차원의 조합으로 구성합니다.

| 축 | 값 |
|----|----|
| 입력 명확도 | 명확(proceed 정답) / 모호(ask 정답) |
| 직무 | 프론트엔드 개발자 / 백엔드 개발자 |
| 주당 가용시간 | 타이트(5h) / 보통(15h) / 여유(25h) |
| 공고 품질 | 충분한 공고 텍스트 / 너무 짧은 공고(needs_rerun 유발) |

```jsonc
// evaluation_set.json (발췌, 실제 파일은 10케이스 전부 포함)
[
  {
    "case_id": "C01",
    "label": "명확_백엔드_공고충분",
    "input": {
      "major": "컴퓨터공학",
      "current_status": "4학년 취준",
      "interests": ["백엔드", "API 설계"],
      "owned_skills": ["Python", "Flask", "MySQL"],
      "target_role": "백엔드 개발자",
      "company_type": "스타트업",
      "weekly_hours": 15,
      "concern": "포트폴리오가 없음",
      "job_posting_text": "FastAPI, PostgreSQL, Docker 경험자 우대 ..."
    },
    "expected_route": "proceed",        // 라우터 정답 레이블
    "expected_rerun": false,            // needs_rerun 정답
    "expected_max_revision": 1,         // Critic이 최대 몇 번 재생성하는지 상한 기대값
    "must_cover_skills": ["FastAPI", "Docker"]  // 최종 로드맵에 반드시 있어야 할 스킬
  },
  {
    "case_id": "C02",
    "label": "모호_직무불분명",
    "input": {
      "major": "경영학",
      "current_status": "대학원 준비 중",
      "interests": ["IT", "기술"],
      "owned_skills": ["Excel", "PowerPoint"],
      "target_role": "IT 관련 업무",        // 모호
      "company_type": null,
      "weekly_hours": 10,
      "concern": "IT로 전직하고 싶은데 뭘 해야 할지 모름",
      "job_posting_text": null
    },
    "expected_route": "ask",
    "expected_rerun": false,
    "expected_max_revision": 2,
    "must_cover_skills": []
  },
  {
    "case_id": "C03",
    "label": "명확_프론트_공고짧음_rerun유발",
    "input": {
      "major": "정보통신공학",
      "current_status": "졸업 예정",
      "interests": ["React", "UI"],
      "owned_skills": ["HTML", "CSS", "JavaScript"],
      "target_role": "프론트엔드 개발자",
      "company_type": "대기업",
      "weekly_hours": 20,
      "concern": null,
      "job_posting_text": "프론트 개발자 구합니다."   // 너무 짧아 evidence_strength=weak 유발
    },
    "expected_route": "proceed",
    "expected_rerun": true,             // gap_analysis가 rerun 트리거
    "expected_max_revision": 1,
    "must_cover_skills": ["React"]
  },
  {
    "case_id": "C04",
    "label": "명확_백엔드_시간타이트",
    "input": {
      "major": "소프트웨어공학",
      "current_status": "취준",
      "interests": ["서버", "인프라"],
      "owned_skills": ["Java", "Spring"],
      "target_role": "백엔드 개발자",
      "company_type": "중견기업",
      "weekly_hours": 5,                // 타이트 → Critic 시간예산 위반 발생 가능성
      "concern": "공부 시간이 부족함",
      "job_posting_text": "Spring Boot, JPA, Redis, Docker, Kubernetes 필수 ..."
    },
    "expected_route": "proceed",
    "expected_rerun": false,
    "expected_max_revision": 2,         // 시간 타이트 → 재생성 가능성 높음
    "must_cover_skills": ["Spring Boot", "Docker"]
  }
  // C05~C10: 유사 구조로 추가 (전공무관 비전공자, returning_user 포함)
]
```

### 4.2 정답 레이블 작성 방법

1. **라우터 정답(`expected_route`):** 두 명 이상의 팀원이 독립적으로 "이 입력이면 묻겠다/진행하겠다"를 판단 → 불일치 시 토론 후 다수결.
2. **`needs_rerun` 정답:** `job_posting_text` 글자 수 < 50 또는 직무 명칭만 있고 역량 없으면 `true`.
3. **`must_cover_skills`:** 공고 텍스트에서 명시된 필수 기술 수동 추출 → 정답 커버 여부 자동 비교.

---

## 5. 데모 시나리오

데모에서는 아래 네 장면을 순서대로 실행해 에이전트의 **라우팅 → 툴 호출 → 검색 보강 → reflection** 네 축을 직관적으로 보여줍니다 (feedback.md 6번 "Why-this-path 트레이스" 제안 반영).

---

### 장면 1. 모호 입력 → ask 경로

**목적:** 자율 라우팅 증명.

```
입력 케이스: C02 (target_role = "IT 관련 업무")

기대 trace:
[onboarding_intake] → [progress_reconciliation] → [triage_router: ambiguity_score=0.82 → ask]
  → [clarify: "프론트엔드·백엔드·데이터 중 관심 분야를 하나 골라주세요."]
  → [triage_router: ambiguity_score=0.21 → proceed]
  → [profile_diagnosis] → ...
```

**확인 포인트:**
- `TraceEntry` 타임라인에 `decision=ask`, 이후 `decision=proceed` 가 순서대로 표시됨.
- `clarify_answers` 리스트에 사용자 답변이 적재됨.
- 최종 로드맵이 clarify 이후 선택된 직무 기준으로 생성됨.

---

### 장면 2. 명확 입력 → proceed 경로

**목적:** 불필요한 역질문 없이 빠른 진행 증명.

```
입력 케이스: C01 (target_role = "백엔드 개발자", 공고 충분)

기대 trace:
[onboarding_intake] → [progress_reconciliation] → [triage_router: ambiguity_score=0.15 → proceed]
  → [profile_diagnosis]
  → [job_requirement: evidence_strength=strong]
  → [gap_analysis: needs_rerun=false]
  → [roadmap_plan: lookup_skill("FastAPI") → known, lookup_skill("Docker") → known]
  → [roadmap_critic: verdict=pass, violations=[]]
  → [finalize]
```

**확인 포인트:**
- `clarify` 노드가 한 번도 호출되지 않음 (ask 경로 미발동).
- `lookup_skill` 호출이 trace에 기록되어 툴 호출 증거 노출.
- `verified=true`, `critic_report.violations=[]`.

---

### 장면 3. 공고 없이 직무만 입력 → web_search로 요구역량 확보

**목적:** 공고 텍스트가 없어도 `web_search`로 요구역량을 보강하는 검색-보강 경로 증명.

```
입력 케이스: C03 변형 (target_role = "프론트엔드 개발자", job_posting_text = null)

기대 trace:
[onboarding_intake] → [triage_router: ambiguity_score=0.18 → proceed]
  → [profile_diagnosis]
  → [job_requirement:
       job_posting_text=null (0자) → 공고 부실 판정
       → web_search("프론트엔드 개발자 채용공고 요구역량 필수기술", k=5) 호출
       tool_called="web_search(프론트엔드 개발자 채용공고 요구역량 필수기술)"
       SearchHit snippet에서 required_skills 추출:
         ["React", "TypeScript", "CSS-in-JS", "REST API", "Git"]
       source="web_search", evidence_strength=medium
       각 스킬에 source_url 부착 (origin="web")]
  → [gap_analysis: needs_rerun=false]
  → [roadmap_plan:
       lookup_skill("React") → known (DB 캐시 히트, 검색 생략)
       lookup_skill("TypeScript") → unknown
         → web_search("TypeScript 학습 강의 튜토리얼 공식문서", k=3)
         tool_called="web_search(TypeScript 학습 튜토리얼 공식문서)"
         SearchHit.url → ResourceItem(origin="web", verified=True)
  → [roadmap_critic: verdict=pass, violations=[]]
  → [finalize: verified=True (db+web origin만 존재, llm origin 없음)]
```

**확인 포인트:**
- `job_requirement` 노드 trace에 `tool_called="web_search(...)"` 가 기록됨 (공고 없이도 요구역량 추출 성공).
- `JobRequirement.source = "web_search"`, `evidence_strength = "medium"`.
- 추출된 스킬 항목마다 `source_url`이 부착되어 있음 (`origin="web"`, `verified=True`).
- `roadmap_plan` trace에 `lookup_skill` unknown → web_search 보강 흐름이 이어짐.
- `FinalOutput.verified=True` (llm origin 없음, db+web만).
- `state["search_count"]` ≤ `MAX_SEARCH=8` 범위 내.
- `state["search_degraded"]=False` (모든 검색 성공).

---

### 장면 4. Critic이 시간초과 로드맵 교정

**목적:** reflection/guardrail 루프 증명.

```
입력 케이스: C04 (weekly_hours=5, 공고에 기술 6개 필수)

1차 roadmap_plan 생성:
  week 1: 8h (예산 초과)
  week 2: 7h (예산 초과)

roadmap_critic 1차 판정:
  verdict = revise
  violations = [
    {type: time_budget_exceeded, detail: "week1 planned_hours=8 > budget=5", location: "week 1"},
    {type: time_budget_exceeded, detail: "week2 planned_hours=7 > budget=5", location: "week 2"}
  ]
  revision_count → 1

roadmap_plan 2차 생성 (위반 사유 주입):
  - 총 기간을 4주→8주로 늘려 주차당 부하 분산
  week 1~8: 모두 planned_hours ≤ 5

roadmap_critic 2차 판정:
  verdict = pass
  violations = []
  revision_count = 1

→ finalize
```

**확인 포인트:**
- 대시보드 trace 타임라인에 `roadmap_critic→roadmap_plan→roadmap_critic` 루프가 표시됨.
- 최종 로드맵의 모든 `WeekPlan.planned_hours ≤ 5`.
- `roadmap.horizon = weeks_8` (동적 기간 산출, Plan-and-Solve 패턴, Wang et al. 2023).
- `revision_count = 1`, `critic_report.verdict = pass`.

---

## 6. 측정 방법

### 6.1 자동화 평가 스크립트 구조

```python
# evaluate.py
import json
from typing import Any

def run_evaluation(eval_set_path: str) -> dict[str, Any]:
    test_cases = json.load(open(eval_set_path))
    results = []

    for tc in test_cases:
        # 그래프 실행
        state = run_graph(OnboardingInput(**tc["input"]))

        result = {
            "case_id": tc["case_id"],
            # KPI 4: 라우터 정확도
            "router_correct": state.route_decision == tc["expected_route"],
            # KPI 5: Hit율
            "tool_hit_rate": tool_hit_rate_from_gap(state.gap_analysis),
            # KPI 1: 커버율
            "gap_coverage": gap_coverage_rate(state.gap_analysis, state.roadmap),
            # KPI 2: 시간예산 위반
            "time_violations": len(time_budget_violations(state.roadmap)),
            # KPI 3: 선후행 위반
            "prereq_violations": len(prereq_order_violations(state.roadmap, SKILL_DB)),
            # KPI 6: 재생성 횟수
            "revision_count": state.revision_count,
            # 부가: needs_rerun 정확도
            "rerun_correct": state.needs_rerun == tc["expected_rerun"],
        }
        results.append(result)

    # 집계
    n = len(results)
    summary = {
        "router_accuracy":       sum(r["router_correct"] for r in results) / n,
        "avg_tool_hit_rate":     sum(r["tool_hit_rate"] for r in results) / n,
        "gap_coverage_all_pass": all(r["gap_coverage"] == 1.0 for r in results),
        "time_violation_total":  sum(r["time_violations"] for r in results),
        "prereq_violation_total":sum(r["prereq_violations"] for r in results),
        "revision_distribution": revision_distribution(results),
    }
    return summary
```

### 6.2 측정 담당 및 시점

| KPI | 측정 담당 | 측정 시점 | 도구 |
|-----|-----------|-----------|------|
| 커버율 | `roadmap_critic` 노드 (자동) | 매 실행 | `gap_coverage_rate()` |
| 시간예산 위반 | `roadmap_critic` 노드 (자동) | 매 실행 | `time_budget_violations()` |
| 선후행 위반 | `roadmap_critic` 노드 (자동) | 매 실행 | `prereq_order_violations()` |
| 라우터 정확도 | 팀원 (평가셋 실행) | 기능 구현 직후·데모 전날 | `evaluate.py` |
| 스킬 DB Hit율 | 팀원 (로그 집계) | 스킬 DB 완성 후 | `evaluate.py` |
| Critic 재생성 분포 | 팀원 (로그 후처리) | 데모 전날 | `evaluate.py` |

### 6.3 측정 결과 보고 형식

```jsonc
// evaluation_result.json (데모 제출용)
{
  "evaluated_at": "2025-XX-XX",
  "n_cases": 10,
  "kpi": {
    "router_accuracy": 0.90,          // 목표 ≥ 0.80
    "gap_coverage_all_pass": true,    // 목표 true
    "time_violation_total": 0,        // 목표 0
    "prereq_violation_total": 0,      // 목표 0
    "avg_tool_hit_rate": 0.78,        // 목표 ≥ 0.70
    "revision_distribution": {
      "0": 0.50,
      "1": 0.40,
      "2": 0.10
    }
  },
  "demo_traces": {
    "C01_proceed": "traces/C01.json",
    "C02_ask":     "traces/C02.json",
    "C04_revision":"traces/C04.json"
  }
}
```

---

## 7. 에이전트 행동 증거 요약 (발표용 체크리스트)

발표 평가자가 "이게 왜 에이전트인가?"를 물을 때 아래 수치로 답합니다.

| 에이전트 특성 | 증거 지표 | 어디서 확인 |
|--------------|-----------|------------|
| 자율 라우팅 | 라우터 정확도 ≥ 80% + ask/proceed 분기 trace | `trace` 타임라인 |
| 도구 호출 | 스킬 DB Hit율 ≥ 70% + `lookup_skill` trace 기록 | `TraceEntry.tool_called` |
| 웹검색 보강 | 공고 없는 케이스에서 `tool_called="web_search(...)"` trace 존재 + `origin="web"` 리소스 url 확인 | `TraceEntry.tool_called`, `ResourceItem.origin` |
| reflection | Critic 위반 발견 후 재생성 성공 케이스 존재 | `revision_count > 0` 케이스 |
| guardrail | 최종 출력 시간예산·선후행 위반 0건 | KPI 2·3 |
| multi-agent 협업 | `needs_rerun=true` 케이스에서 Job 재요청 trace 존재 | `TraceEntry.decision=rerun_job` |
| episodic memory | returning_user 케이스에서 `decision=reconcile` trace 존재 | `TraceEntry.decision` |

---

## 참고 문헌

- Anthropic, *Building Effective Agents* (2024) — workflow vs. agent 분류 기준.
- Yao et al., *ReAct: Synergizing Reasoning and Acting in Language Models* (2022) — 툴 호출로 환각 억제.
- Shinn et al., *Reflexion: Language Agents with Verbal Reinforcement Learning* (2023) — reflection 루프 설계 근거.
- Madaan et al., *Self-Refine: Iterative Refinement with Self-Feedback* (2023) — 단일 모델 자기 개선 루프.
- Wang et al., *Plan-and-Solve Prompting* (2023) — 동적 기간 산출(task decomposition) 근거.
- LangGraph Documentation, *Conditional Edges & Graph State* — 조건 엣지·루프 구현.
