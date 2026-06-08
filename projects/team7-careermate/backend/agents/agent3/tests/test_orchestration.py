"""run_agent3 전체 파이프라인 (키 없음 폴백) — 노드 순서/finalize/재방문/revise 종료."""

from __future__ import annotations

import asyncio

from agents.agent3.constants import MAX_REVISIONS
from agents.agent3.pipeline import run_agent3
from agents.agent3.models import (
    CriticVerdict,
    EpisodicMemory,
    MemoryStatus,
    Roadmap,
    WeeklyProgress,
    WeekPlan,
)


def _run(coro):
    return asyncio.run(coro)


def test_full_pipeline_new_user(profile_frontend, job_frontend):
    st = _run(run_agent3(profile_frontend, job_frontend, weekly_hours=8))
    nodes = [t.node for t in st.trace]
    assert nodes[0] == "progress_reconciliation"
    assert nodes[-1] == "finalize"
    assert {"gap_analysis", "roadmap_plan", "roadmap_critic"} <= set(nodes)

    fo = st.final_output
    assert fo is not None
    # 규칙 폴백 패커는 critic을 만족 → pass, 재생성 0
    assert st.critic_report.verdict == CriticVerdict.pass_
    assert st.revision_count == 0
    # FinalOutput 무결성
    covered = set()
    for w in fo.roadmap.weeks:
        covered.update(w.covered_skills)
    for g in fo.gap_analysis.gaps:
        assert g.skill in covered
    # trace_summary가 finalize까지 포함
    assert fo.trace_summary[-1].node == "finalize"
    assert fo.disclaimer


def test_revise_loop_terminates(profile_frontend, job_frontend):
    st = _run(run_agent3(profile_frontend, job_frontend, weekly_hours=8))
    # 항상 pass이거나 MAX_REVISIONS에서 강제 종료
    assert st.critic_report.verdict == CriticVerdict.pass_ or st.revision_count == MAX_REVISIONS
    assert st.revision_count <= MAX_REVISIONS


def test_returning_user_reconcile(profile_frontend, job_frontend):
    prev = Roadmap(
        weekly_hours_budget=8,
        total_weeks=2,
        weeks=[
            WeekPlan(week_index=1, covered_skills=["React"], planned_hours=8),
            WeekPlan(week_index=2, covered_skills=["TypeScript"], planned_hours=8),
        ],
    )
    mem = EpisodicMemory(
        status=MemoryStatus.returning_user,
        last_roadmap=prev,
        weekly_progress=[
            WeeklyProgress(week_index=1, completed=True),
            WeeklyProgress(week_index=2, completed=False),
        ],
        last_updated="2025-01-01",
    )
    st = _run(run_agent3(profile_frontend, job_frontend, weekly_hours=8, episodic_memory=mem))
    assert st.completed_skills == ["React"]
    assert st.carry_over_skills == ["TypeScript"]
    recon = next(t for t in st.trace if t.node == "progress_reconciliation")
    assert recon.decision == "reconcile"


def test_new_user_skips_reconcile(profile_frontend, job_frontend):
    st = _run(run_agent3(profile_frontend, job_frontend, weekly_hours=8))
    recon = next(t for t in st.trace if t.node == "progress_reconciliation")
    assert recon.decision == "skip_reconcile"
