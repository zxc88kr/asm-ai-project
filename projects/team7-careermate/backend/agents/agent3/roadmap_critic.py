"""roadmap_critic 노드 — 4종 체크리스트 자가 검증 (Reflexion + 런타임 가드레일).

4종 위반(ViolationType):
  ① uncovered_gap          : 모든 gap 스킬이 어느 주차의 covered_skills에 ≥1회 포함되는가
  ② time_budget_exceeded   : 각 주차 planned_hours ≤ weekly_hours_budget
  ③ prereq_order_violation : (최초 등장 기준) 선행 스킬의 '첫 등장 주차' ≤ 후행의 '첫 등장 주차'
  ④ forbidden_phrase       : 합격/취업 단정 등 금칙 표현 없음

모두 LLM 없이 코드로 검증한다(결정론적·무료). 위반이 있으면 verdict=revise →
조건 엣지가 roadmap_plan으로 되돌린다(최대 MAX_REVISIONS회). revision_count 증가는
조건 엣지/orchestrator 책임(CANON E) — 이 노드는 검증·판정만 한다.

③ 기준 결정: docs 의사코드의 '마지막 등장' 대신 '최초 등장'을 사용한다. 같은 스킬을
나중 주차에 복습 배치해도 위반으로 잡지 않아 불필요한 revise 루프를 막고, 교육적으로도
'선행을 먼저 시작했는가'가 올바른 기준이기 때문이다.

설계 근거: docs/02-agent-graph.md §7, docs/05-reflection-critic.md.
"""

from __future__ import annotations

from .constants import FORBIDDEN_PHRASES
from .models import (
    CriticReport,
    CriticVerdict,
    GapItem,
    Roadmap,
    SkillRecord,
    Violation,
    ViolationType,
)
from .state import Agent3State, append_trace
from .tools import lookup_skill, normalize_skill_name


def check_roadmap(
    roadmap: Roadmap,
    gaps: list[GapItem],
    weekly_hours: int,
    skill_records: dict[str, SkillRecord] | None = None,
) -> CriticReport:
    """4종 체크리스트를 돌려 CriticReport를 반환한다(순수 함수, throw 금지)."""
    skill_records = skill_records or {}
    violations: list[Violation] = []

    weeks = sorted(roadmap.weeks, key=lambda w: w.week_index)
    weekly_budget = roadmap.weekly_hours_budget or weekly_hours

    # ── ① 부족역량 커버율 ──────────────────────────────────────
    covered: set[str] = set()
    for w in weeks:
        covered.update(w.covered_skills)
    for g in gaps:
        if g.skill not in covered:
            violations.append(
                Violation(
                    type=ViolationType.uncovered_gap,
                    detail=f"{g.skill}가 로드맵 어느 주차에도 매핑되지 않음",
                    location="roadmap.weeks",
                )
            )

    # ── ② 주차 시간 예산 ───────────────────────────────────────
    for w in weeks:
        if w.planned_hours > weekly_budget:
            violations.append(
                Violation(
                    type=ViolationType.time_budget_exceeded,
                    detail=f"{w.week_index}주차 {w.planned_hours}h > 예산 {weekly_budget}h",
                    location=f"week {w.week_index}",
                )
            )

    # ── ③ 선후행 순서 (최초 등장 기준) ─────────────────────────
    first_week: dict[str, int] = {}
    for w in weeks:  # week_index 오름차순
        for skill in w.covered_skills:
            if skill not in first_week:
                first_week[skill] = w.week_index
    for skill, s_week in first_week.items():
        record = skill_records.get(skill) or lookup_skill(normalize_skill_name(skill))
        for prereq in record.prereqs:
            p_week = first_week.get(prereq)
            if p_week is not None and p_week > s_week:
                violations.append(
                    Violation(
                        type=ViolationType.prereq_order_violation,
                        detail=(
                            f"{skill}의 선행 {prereq}가 더 늦게 시작됨"
                            f"(선행 {p_week}주차 > {skill} {s_week}주차)"
                        ),
                        location=f"week {s_week}",
                    )
                )

    # ── ④ 금칙 표현 ───────────────────────────────────────────
    roadmap_text = roadmap.model_dump_json()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in roadmap_text:
            violations.append(
                Violation(
                    type=ViolationType.forbidden_phrase,
                    detail=f"금칙 표현 발견: '{phrase}'",
                    location="roadmap 텍스트",
                )
            )

    verdict = CriticVerdict.pass_ if not violations else CriticVerdict.revise
    return CriticReport(verdict=verdict, violations=violations, checked_at_revision=0)


def run_roadmap_critic(state: Agent3State) -> Agent3State:
    """roadmap_critic 노드 본문. check_roadmap을 state에 연결하고 trace를 남긴다."""
    roadmap = state.roadmap
    gaps = state.gap_analysis.gaps if state.gap_analysis else []

    if roadmap is None:
        report = CriticReport(verdict=CriticVerdict.pass_, violations=[], checked_at_revision=state.revision_count)
    else:
        report = check_roadmap(roadmap, gaps, state.weekly_hours, state.skill_records)
        report.checked_at_revision = state.revision_count

    state.critic_report = report

    by_type: dict[str, int] = {}
    for v in report.violations:
        by_type[v.type.value] = by_type.get(v.type.value, 0) + 1
    summary = ", ".join(f"{k}={n}" for k, n in by_type.items()) or "위반 없음"

    append_trace(
        state,
        "roadmap_critic",
        input_summary=f"revision_count={state.revision_count}, weeks={roadmap.total_weeks if roadmap else 0}",
        decision=report.verdict.value,
        output_summary=f"verdict={report.verdict.value}, violations=[{summary}]",
    )
    return state
