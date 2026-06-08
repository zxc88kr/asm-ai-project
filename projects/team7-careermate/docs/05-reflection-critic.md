# Roadmap Critic / Reflection 루프

이 문서는 CareerMate 에이전트 그래프의 **자기 검증 노드(`roadmap_critic`)** 를 설명합니다.
로드맵을 사용자에게 전달하기 *전에* 에이전트 스스로 4가지 기준으로 점검하고, 문제가 있으면 자동으로 다시 만드는 루프입니다.
이를 통해 **reflection(자기 반성)** 과 **guardrails(출력 제한 규칙 강제)** 를 한 노드에서 동시에 달성합니다.

---

## 1. 왜 Critic 노드가 필요한가

### 1-1. 선언만으로는 부족한 가드레일

원본 기획 4페이지는 '합격 가능성 단정 금지', '진로 최종 결정 금지'를 명시했지만, 이를 런타임에 강제하는 장치가 없었습니다. 프롬프트 한 줄은 LLM이 어기기 쉽습니다.

> "guardrail = 프롬프트 지시"가 아니라 "guardrail = 출력 후 구조·내용 검증 노드"
> — feedback.md 6페이지 상세 피드백

### 1-2. 에이전트의 자기 교정 능력

**Reflexion (Shinn et al., 2023)** 은 에이전트가 자신의 출력을 언어적으로 비판·반영하고 재시도해 품질을 높이는 self-reflection 루프를 제안합니다.
**Self-Refine (Madaan et al., 2023)** 은 별도 모델 없이 동일 모델이 자기 피드백으로 반복 개선하는 방법을 보입니다.

Critic 노드는 이 두 논문의 패턴을 1.5주 범위에서 실현 가능한 최소 단위로 구현합니다.
로드맵이 기준을 통과하지 못하면 위반 사유를 담아 `roadmap_plan` 노드로 되돌리고, 최대 2회 재생성 후 통과 여부와 무관하게 종료합니다.

---

## 2. Critic 노드 위치 (그래프 흐름)

전체 그래프 구조는 [에이전트 그래프](02-agent-graph.md)를 참고하세요.

```
roadmap_plan
     │
     ▼
roadmap_critic ──[revise & revision_count < 2]──► roadmap_plan
     │
     [pass OR revision_count >= 2]
     │
     ▼
  finalize
```

| 조건 | 다음 노드 |
|---|---|
| `critic_verdict == "pass"` | `finalize` |
| `critic_verdict == "revise"` AND `revision_count < MAX_REVISIONS` | `roadmap_plan` (루프백) |
| `revision_count >= MAX_REVISIONS` | `finalize` (best-effort + 경고 플래그) |

`MAX_REVISIONS = 2` — 무한 루프 방지 상수.

---

## 3. 체크리스트 4종 — 의사코드

### 3-1. 전체 흐름

```python
def roadmap_critic(state: CareerMateState) -> CareerMateState:
    roadmap: Roadmap = state["roadmap"]
    gap_analysis: GapAnalysis = state["gap_analysis"]
    weekly_hours: int = state["onboarding_input"].weekly_hours

    violations: list[Violation] = []

    # 체크 1: 부족역량 커버율
    violations += check_coverage(roadmap, gap_analysis)

    # 체크 2: 주차 시간 예산
    violations += check_time_budget(roadmap, weekly_hours)

    # 체크 3: 선후행 순서
    violations += check_prereq_order(roadmap)

    # 체크 4: 금칙 표현
    violations += check_forbidden_phrases(roadmap)

    if violations:
        verdict = "revise"
    else:
        verdict = "pass"

    report = CriticReport(
        verdict=verdict,
        violations=violations,
        checked_at_revision=state["revision_count"],
    )
    state["critic_report"] = report

    # 분기 결정 트레이스
    decision = "pass" if verdict == "pass" else "revise"
    state["trace"].append(TraceEntry(
        node="roadmap_critic",
        input_summary=f"weeks={roadmap.total_weeks}, gaps={len(gap_analysis.gaps)}",
        decision=decision,
        tool_called=None,
        output_summary=f"verdict={verdict}, violations={len(violations)}",
        ts=now_iso(),
    ))

    return state
```

---

### 3-2. 체크 1 — 부족역량 커버율 (coverage)

**목표:** `gap_analysis.gaps`에 있는 모든 부족 스킬이 최소 1개 주차에 매핑되어야 합니다.

```python
def check_coverage(
    roadmap: Roadmap,
    gap_analysis: GapAnalysis,
) -> list[Violation]:
    """모든 GapItem.skill이 roadmap 어딘가의 covered_skills에 포함되는지 확인."""
    covered: set[str] = set()
    for week in roadmap.weeks:
        covered.update(week.covered_skills)

    violations = []
    for gap in gap_analysis.gaps:
        if gap.skill not in covered:
            violations.append(Violation(
                type="uncovered_gap",
                detail=f"부족역량 '{gap.skill}'이 로드맵 어느 주차에도 배정되지 않음",
                location=f"gap: {gap.skill}",
            ))
    return violations
```

> **왜 필요한가:** 갭이 로드맵에 빠지면 사용자는 핵심 준비를 놓칩니다.
> 8페이지 KPI의 '부족 역량 커버율(%)' 지표를 에이전트가 자가 계산하는 지점입니다.

---

### 3-3. 체크 2 — 주차 시간 예산 (time budget)

**목표:** 각 주차의 `planned_hours`가 사용자 가용 시간(`weekly_hours`)을 초과하지 않아야 합니다.

```python
def check_time_budget(
    roadmap: Roadmap,
    weekly_hours: int,
) -> list[Violation]:
    """주차별 계획 시간이 사용자 주당 가용 시간을 넘지 않는지 확인."""
    violations = []
    for week in roadmap.weeks:
        if week.planned_hours > weekly_hours:
            violations.append(Violation(
                type="time_budget_exceeded",
                detail=(
                    f"week {week.week_index}: 계획 {week.planned_hours}h"
                    f" > 가용 {weekly_hours}h"
                ),
                location=f"week {week.week_index}",
            ))
    return violations
```

> **왜 필요한가:** "주 5시간 가용"인 사용자에게 "주 20시간짜리" 로드맵을 내놓는 모순을
> 시스템이 스스로 잡지 못하면 에이전트라 부르기 어렵습니다 (feedback.md §3).

---

### 3-4. 체크 3 — 선후행 순서 (prereq order)

**목표:** 주차 배치가 Skill DB의 `prereqs`(선행 스킬) 순서를 따라야 합니다.
예: `React`를 배우려면 `JavaScript`가 먼저 나와야 합니다.

```python
def check_prereq_order(roadmap: Roadmap) -> list[Violation]:
    """
    선행 스킬 주차가 해당 스킬 주차보다 늦으면(prereq_week > week_index) 위반.
    즉 스킬은 선행 스킬과 같은 주차이거나 그 이후 주차여야 정상이다(같은 주차 동시 학습 허용).
    lookup_skill로 prereqs를 가져옴.
    """
    # 스킬 → 처음 등장 주차 인덱스 매핑 구성
    skill_to_week: dict[str, int] = {}
    for week in roadmap.weeks:
        for skill in week.covered_skills:
            if skill not in skill_to_week:
                skill_to_week[skill] = week.week_index

    violations = []
    for skill, week_idx in skill_to_week.items():
        normalized = normalize_skill_name(skill)
        record: SkillRecord = lookup_skill(normalized)
        if record.status == "unknown":
            continue  # 사전 없는 스킬은 검사 생략 (폴백; 웹검색으로 보강된 스킬도 prereqs 미보장이므로 동일하게 skip)

        for prereq in record.prereqs:
            prereq_normalized = normalize_skill_name(prereq)
            prereq_week = skill_to_week.get(prereq_normalized)
            if prereq_week is None:
                # 선행 스킬이 로드맵에 아예 없음 → uncovered_gap과 중복 가능
                continue
            if prereq_week > week_idx:
                violations.append(Violation(
                    type="prereq_order_violation",
                    detail=(
                        f"'{skill}'(week {week_idx})가 선행 '{prereq}'(week {prereq_week})보다 앞에 배치됨"
                    ),
                    location=f"week {week_idx}: {skill}",
                ))
    return violations
```

> **왜 필요한가:** Skill DB의 선후행 정보(`lookup_skill`의 `prereqs`)를 활용해 로드맵이
> "React 배우는데 JavaScript 아직 안 나옴" 같은 논리적 오류를 스스로 잡습니다.
> ReAct 패턴에서 도구 호출 결과를 검증 루프에 재활용하는 방식입니다 (Yao et al., 2022).

---

### 3-5. 체크 4 — 금칙 표현 (forbidden phrases)

**목표:** 로드맵 텍스트에 아래 금칙 표현이 포함되면 재생성 대상입니다.

#### 금칙 표현 룰 리스트

원본 기획 4페이지 "에이전트가 하지 않는 범위"를 기반으로 런타임 강제 규칙으로 변환합니다.

| 번호 | 카테고리 | 금칙 패턴 (부분 일치) | 이유 |
|---|---|---|---|
| F-01 | 합격 단정 | `"합격"`, `"취업 보장"`, `"100% 합격"`, `"붙을 수 있"` | 합격 가능성 단정 금지 |
| F-02 | 합격 단정 | `"이 로드맵만 따르면"`, `"따라하면 합격"` | 합격 단정 문구 변형 |
| F-03 | 진로 결정 | `"이 직무가 맞습니다"`, `"이 길이 맞다"`, `"적성에 맞으니"` | 진로 최종 결정 금지 |
| F-04 | 진로 결정 | `"커리어는 반드시"`, `"진로를 확정"` | 진로 단정 |
| F-05 | 연봉·처우 단정 | `"연봉"`, `"억대"`, `"고연봉"` | 처우 단정 금지 |
| F-06 | 기업 단정 | `"네카라쿠배 입사"`, `"대기업 입사 가능"` | 특정 기업 합격 단정 |
| F-07 | 과장 수식 | `"무조건"`, `"반드시 성공"`, `"완벽한 로드맵"` | 과장 표현 |
| F-08 | 실시간 정보 | `"현재 채용 중"`, `"지금 공고"` | 실시간 크롤링 비범위 (LLM 환각 차단) |

```python
FORBIDDEN_PHRASES: list[str] = [
    "합격",
    "취업 보장",
    "100% 합격",
    "붙을 수 있",
    "이 로드맵만 따르면",
    "따라하면 합격",
    "이 직무가 맞습니다",
    "이 길이 맞다",
    "적성에 맞으니",
    "커리어는 반드시",
    "진로를 확정",
    "억대",
    "고연봉",
    "네카라쿠배 입사",
    "대기업 입사 가능",
    "무조건",
    "반드시 성공",
    "완벽한 로드맵",
    "현재 채용 중",
    "지금 공고",
]

def _extract_all_text(roadmap: Roadmap) -> list[tuple[str, str]]:
    """(텍스트, 위치 레이블) 튜플 리스트로 로드맵 전체 텍스트 추출."""
    items = []
    items.append((roadmap.rationale, "roadmap.rationale"))
    for week in roadmap.weeks:
        for obj in week.objectives:
            items.append((obj, f"week {week.week_index}.objectives"))
        for task in week.tasks:
            items.append((task.title, f"week {week.week_index}.task: {task.title}"))
    return items

def check_forbidden_phrases(roadmap: Roadmap) -> list[Violation]:
    """로드맵 텍스트 전체에서 금칙 표현 탐지."""
    violations = []
    for text, location in _extract_all_text(roadmap):
        for phrase in FORBIDDEN_PHRASES:
            if phrase in text:
                violations.append(Violation(
                    type="forbidden_phrase",
                    detail=f"금칙 표현 '{phrase}' 발견",
                    location=location,
                ))
                break  # 같은 위치에서 중복 위반 1개만 보고
    return violations
```

> **왜 필요한가:** 4페이지의 "하지 않는 범위" 선언이 프롬프트 지시에서 **런타임 검증 규칙**으로 승격됩니다.
> 선언적 가드레일의 한계를 실행 가능한 노드로 보완하는 핵심 지점입니다 (feedback.md §6).

---

## 4. Conditional Edge — LangGraph 구현 패턴

```python
from langgraph.graph import StateGraph, END

MAX_REVISIONS: int = 2

def route_after_critic(state: CareerMateState) -> str:
    """
    roadmap_critic 이후 다음 노드를 결정하는 conditional edge 함수.
    반환값은 graph.add_conditional_edges의 mapping 키와 일치해야 함.
    """
    report: CriticReport = state["critic_report"]
    revision_count: int = state["revision_count"]

    if report.verdict == "pass":
        return "finalize"
    if revision_count >= MAX_REVISIONS:
        # 최대 재시도 초과: best-effort로 finalize, verified=False 경고
        state["verified"] = False
        return "finalize"
    # revise: revision_count 증가 후 roadmap_plan으로 루프백
    state["revision_count"] += 1
    return "roadmap_plan"

# 그래프 엣지 연결 예시
builder = StateGraph(CareerMateState)
# ... 노드 추가 생략 ...

builder.add_conditional_edges(
    "roadmap_critic",
    route_after_critic,
    {
        "revise": "roadmap_plan",
        "pass": "finalize",
    },
)
```

> **LangGraph 공식 패턴:** `add_conditional_edges`의 두 번째 인자로 상태를 받아 다음 노드 이름을 반환하는 함수를 넘깁니다. `mapping` 딕셔너리로 반환값 → 노드 이름을 명시적으로 선언해 그래프가 가능한 경로를 사전에 알 수 있게 합니다.

---

## 5. roadmap_plan — revise 수신 처리

Critic이 `revise`를 돌려보낼 때 `roadmap_plan`은 위반 내용을 입력 컨텍스트로 주입받아 재생성합니다.

```python
def roadmap_plan(state: CareerMateState) -> CareerMateState:
    critic_report: CriticReport | None = state.get("critic_report")

    revision_context = ""
    if critic_report and critic_report.violations:
        # 위반 사유를 프롬프트 컨텍스트로 변환
        violation_lines = [
            f"- [{v.type}] {v.detail} (위치: {v.location})"
            for v in critic_report.violations
        ]
        revision_context = (
            "이전 로드맵에서 다음 위반이 발견되었습니다. 반드시 수정하세요:\n"
            + "\n".join(violation_lines)
        )

    # LLM 프롬프트에 revision_context 주입
    roadmap: Roadmap = call_llm_for_roadmap(
        gap_analysis=state["gap_analysis"],
        onboarding_input=state["onboarding_input"],
        episodic_memory=state.get("episodic_memory"),
        revision_context=revision_context,       # ← revise 시 채워짐
        skill_db_lookup_fn=lookup_skill,
    )

    state["roadmap"] = roadmap
    state["trace"].append(TraceEntry(
        node="roadmap_plan",
        input_summary=f"revision #{state['revision_count']}, violations={len(critic_report.violations) if critic_report else 0}",
        decision=None,
        tool_called="lookup_skill",
        output_summary=f"roadmap generated: {roadmap.total_weeks}weeks",
        ts=now_iso(),
    ))
    return state
```

---

## 6. Pydantic 모델

```python
from pydantic import BaseModel
from typing import Literal

ViolationType = Literal[
    "uncovered_gap",
    "time_budget_exceeded",
    "prereq_order_violation",
    "forbidden_phrase",
]
CriticVerdict = Literal["pass", "revise"]


class Violation(BaseModel):
    type: ViolationType           # 위반 유형
    detail: str                   # 위반 상세 설명
    location: str                 # 위반 발생 위치 (예: "week 3" / "gap: React")


class CriticReport(BaseModel):
    verdict: CriticVerdict        # "pass" | "revise"
    violations: list[Violation]   # 위반 목록 (pass이면 빈 리스트)
    checked_at_revision: int      # 검증 시점의 revision_count
```

---

## 7. CriticReport JSON 예시

### 예시 A — revise (위반 2건)

```json
{
  "verdict": "revise",
  "violations": [
    {
      "type": "uncovered_gap",
      "detail": "부족역량 'Docker'이 로드맵 어느 주차에도 배정되지 않음",
      "location": "gap: Docker"
    },
    {
      "type": "time_budget_exceeded",
      "detail": "week 3: 계획 12h > 가용 8h",
      "location": "week 3"
    }
  ],
  "checked_at_revision": 0
}
```

### 예시 B — pass (위반 없음)

```json
{
  "verdict": "pass",
  "violations": [],
  "checked_at_revision": 1
}
```

### 예시 C — 최대 재시도 초과 (best-effort finalize)

`revision_count >= MAX_REVISIONS(=2)` 도달 시: `verdict == "revise"`이지만 `finalize`로 강제 진행하고
`State.verified = false`를 설정합니다. 사용자 출력에는 아래와 같은 경고가 추가됩니다.

```json
{
  "disclaimer": "이 로드맵은 일부 기준을 충족하지 못한 상태로 생성되었습니다. 주차별 시간 및 선수학습 순서를 직접 확인하세요.",
  "verified": false
}
```

---

## 8. 전체 Critic 루프 실행 시나리오

```
[roadmap_plan] → 로드맵 생성 (revision_count=0)
      ↓
[roadmap_critic] → check 4종 실행
  violation: time_budget_exceeded (week3: 12h > 8h)
  verdict: "revise"
      ↓
[roadmap_plan] → revision_context에 위반 주입, 재생성 (revision_count=1)
      ↓
[roadmap_critic] → check 4종 재실행
  violations: []
  verdict: "pass"
      ↓
[finalize] → verified=True, final_output 조립 → END
```

**최대 재시도 도달 시나리오:**
```
[roadmap_critic] verdict="revise" (revision_count=2 = MAX_REVISIONS)
      ↓
route_after_critic → "finalize" (강제)
[finalize] → verified=False, disclaimer 첨부 → END
```

---

## 9. 상태 키 흐름 요약

| 상태 키 | roadmap_plan 쓰기 | roadmap_critic 쓰기 | finalize 읽기 |
|---|---|---|---|
| `roadmap` | 생성/덮어쓰기 | - | 읽기 |
| `critic_report` | - | 생성/덮어쓰기 | 읽기 |
| `revision_count` | - | 증가 (route 함수에서) | 읽기 |
| `verified` | - | `False` 설정 (초과 시) | 읽기 |
| `trace` | append | append | 읽기 (요약) |

---

## 10. KPI 자동화 연결

8페이지 KPI 항목을 Critic 노드가 자동으로 측정합니다.

| KPI 항목 | Critic 검사 항목 | 측정 방법 |
|---|---|---|
| 로드맵 구체성 평가 | 부족역량 커버율 | `uncovered_gap` 위반 0건 |
| 로드맵 생성 성공률 | 전체 위반 0건 | `verdict == "pass"` |
| 시간 현실성 | 주차 예산 준수 | `time_budget_exceeded` 위반 0건 |
| 가드레일 준수율 | 금칙 표현 없음 | `forbidden_phrase` 위반 0건 |

> 이 지표들은 에이전트가 매 실행마다 자가 계산하므로 수동 평가 없이 측정 가능합니다.

---

## 11. 이론적 근거 요약

| 개념 | 논문/출처 | 이 구현에서의 역할 |
|---|---|---|
| Self-Reflection 루프 | Reflexion (Shinn et al., 2023) | Critic → roadmap_plan 루프백 구조 |
| 자기 피드백 개선 | Self-Refine (Madaan et al., 2023) | 위반 사유를 프롬프트로 재주입하는 revision_context |
| 동적 계획 분해 | Plan-and-Solve (Wang et al., 2023) | roadmap_plan의 갭 기반 동적 주차 산출 |
| 도구 호출 검증 | ReAct (Yao et al., 2022) | check_prereq_order에서 lookup_skill 결과 재활용 |
| Conditional Edge | LangGraph 공식 문서 | `add_conditional_edges`로 pass/revise/force-finalize 분기 |
| Guardrails 런타임 강제 | Building Effective Agents (Anthropic, 2024) | 금칙 표현·스키마 검증을 노드로 구현 |

---

## 관련 문서

- [에이전트 그래프 전체 구조](02-agent-graph.md)
- [에이전트 계약 / Triage·State 스키마](03-agent-contracts.md)
- [Skill DB 조회 툴 및 web_search 계약](04-tools-skill-db.md)
