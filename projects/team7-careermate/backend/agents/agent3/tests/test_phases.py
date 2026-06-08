"""build_phases — 항상 정확히 4단계로 균등 분할 (UI 카드 고정)."""

from __future__ import annotations

from agents.agent3.llm import TARGET_PHASES, build_phases
from agents.agent3.models import ResourceItem, SourceOrigin, TaskItem, WeekPlan


def _week(idx, phase, skills):
    return WeekPlan(
        week_index=idx,
        phase=phase,
        covered_skills=skills,
        planned_hours=8,
        tasks=[
            TaskItem(
                title=f"{s} 학습",
                skill=s,
                est_hours=4,
                resources=[ResourceItem(title="r", url="https://x", verified=True, origin=SourceOrigin.db)],
            )
            for s in skills
        ],
    )


def test_eight_weeks_split_into_four_even_phases():
    weeks = [
        _week(1, "기초 다지기", ["JavaScript"]),
        _week(2, "기초 다지기", ["JavaScript"]),
        _week(3, "핵심 역량 강화", ["React"]),
        _week(4, "핵심 역량 강화", ["React"]),
        _week(5, "프로젝트 실전", ["TypeScript"]),
        _week(6, "프로젝트 실전", ["TypeScript"]),
        _week(7, "포트폴리오 & 준비", ["상태관리"]),
        _week(8, "포트폴리오 & 준비", ["상태관리"]),
    ]
    phases = build_phases(weeks)
    assert len(phases) == 4
    # 8주 → 2·2·2·2 균등
    assert [(p.week_from, p.week_to) for p in phases] == [(1, 2), (3, 4), (5, 6), (7, 8)]
    # 라벨 그대로 제목
    assert [p.title for p in phases] == ["기초 다지기", "핵심 역량 강화", "프로젝트 실전", "포트폴리오 & 준비"]


def test_always_four_phases_even_without_labels():
    weeks = [_week(i, None, ["React"]) for i in range(1, 9)]  # 라벨 없음
    phases = build_phases(weeks)
    assert len(phases) == 4
    assert [(p.week_from, p.week_to) for p in phases] == [(1, 2), (3, 4), (5, 6), (7, 8)]
    # 라벨 없으면 표준 4제목
    assert [p.title for p in phases] == ["기초 다지기", "핵심 역량 강화", "프로젝트 실전", "포트폴리오 & 준비"]


def test_six_weeks_balanced_2_2_1_1():
    weeks = [_week(i, None, ["React"]) for i in range(1, 7)]
    phases = build_phases(weeks)
    assert len(phases) == 4
    assert [(p.week_from, p.week_to) for p in phases] == [(1, 2), (3, 4), (5, 5), (6, 6)]


def test_unique_titles_no_duplicates():
    # 라벨이 한 종류뿐이어도 4개 카드 제목이 중복되지 않아야
    weeks = [_week(i, "기초 다지기", ["React"]) for i in range(1, 9)]
    phases = build_phases(weeks)
    titles = [p.title for p in phases]
    assert len(set(titles)) == 4


def test_checklist_item_ids_and_no_completed():
    weeks = [_week(1, "기초", ["JavaScript", "HTML/CSS"]), _week(2, "기초", ["React"])]
    phases = build_phases(weeks, target=2)
    items = phases[0].items
    assert items[0].id == "p1-i1"
    assert items[0].resources and items[0].resources[0].verified is True
    assert not hasattr(items[0], "completed")


def test_fewer_weeks_than_target():
    weeks = [_week(1, None, ["React"]), _week(2, None, ["TypeScript"])]
    phases = build_phases(weeks)  # 2주 < 4 → 2단계
    assert len(phases) == 2


def test_target_constant_is_four():
    assert TARGET_PHASES == 4


def test_empty_weeks():
    assert build_phases([]) == []
