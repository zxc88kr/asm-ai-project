"""roadmap_critic.py — 4종 체크리스트 + 완화된 선후행(최초 등장) 기준."""

from __future__ import annotations

from agents.agent3.models import (
    CriticVerdict,
    GapItem,
    PriorityLevel,
    ResourceItem,
    Roadmap,
    RoadmapHorizon,
    SkillStatus,
    SourceOrigin,
    TaskItem,
    ViolationType,
    WeekPlan,
)
from agents.agent3.roadmap_critic import check_roadmap
from agents.agent3.tools import lookup_skill

RECORDS = {
    s: lookup_skill(s)
    for s in ["JavaScript", "HTML/CSS", "React", "TypeScript", "상태관리", "Docker"]
}


def _task(skill, h):
    return TaskItem(
        title=skill,
        skill=skill,
        est_hours=h,
        resources=[ResourceItem(title="r", url="https://x", verified=True, origin=SourceOrigin.db)],
        verified=True,
    )


def _week(idx, sh):
    return WeekPlan(
        week_index=idx,
        objectives=[s for s, _ in sh],
        tasks=[_task(s, h) for s, h in sh],
        covered_skills=[s for s, _ in sh],
        planned_hours=sum(h for _, h in sh),
    )


def _gap(s):
    return GapItem(skill=s, priority=PriorityLevel.high, skill_status=SkillStatus.known, verified=True)


def _types(report):
    return {v.type for v in report.violations}


def test_pass_clean_roadmap():
    rm = Roadmap(
        horizon=RoadmapHorizon.weeks_4,
        total_weeks=4,
        weekly_hours_budget=8,
        weeks=[
            _week(1, [("JavaScript", 8)]),
            _week(2, [("HTML/CSS", 8)]),
            _week(3, [("React", 8)]),
            _week(4, [("React", 4), ("TypeScript", 4)]),
        ],
    )
    rep = check_roadmap(rm, [_gap("React"), _gap("TypeScript")], 8, RECORDS)
    assert rep.verdict == CriticVerdict.pass_
    assert rep.violations == []


def test_relaxed_prereq_allows_review_placement():
    # React를 week2 도입 후 week4 복습(상태관리 week3 뒤) → 위반 아님 (최초 등장 기준)
    rm = Roadmap(
        weekly_hours_budget=8,
        total_weeks=4,
        weeks=[
            _week(1, [("JavaScript", 8)]),
            _week(2, [("React", 8)]),
            _week(3, [("상태관리", 8)]),
            _week(4, [("React", 8)]),
        ],
    )
    rep = check_roadmap(rm, [_gap("React"), _gap("상태관리")], 8, RECORDS)
    assert ViolationType.prereq_order_violation not in _types(rep)


def test_violation_uncovered_gap():
    rm = Roadmap(weekly_hours_budget=8, total_weeks=1, weeks=[_week(1, [("React", 8)])])
    rep = check_roadmap(rm, [_gap("React"), _gap("Docker")], 8, RECORDS)
    assert ViolationType.uncovered_gap in _types(rep)


def test_violation_time_budget():
    rm = Roadmap(weekly_hours_budget=8, total_weeks=1, weeks=[_week(1, [("React", 12)])])
    rep = check_roadmap(rm, [_gap("React")], 8, RECORDS)
    assert ViolationType.time_budget_exceeded in _types(rep)


def test_violation_prereq_order():
    # 선행 JavaScript를 후행 React보다 늦게 처음 도입 → 위반
    rm = Roadmap(
        weekly_hours_budget=8,
        total_weeks=2,
        weeks=[_week(1, [("React", 8)]), _week(2, [("JavaScript", 8)])],
    )
    rep = check_roadmap(rm, [_gap("React")], 8, RECORDS)
    assert ViolationType.prereq_order_violation in _types(rep)


def test_violation_forbidden_phrase():
    rm = Roadmap(
        weekly_hours_budget=8,
        total_weeks=1,
        rationale="이대로 하면 합격 가능합니다",
        weeks=[_week(1, [("React", 8)])],
    )
    rep = check_roadmap(rm, [_gap("React")], 8, RECORDS)
    assert ViolationType.forbidden_phrase in _types(rep)
