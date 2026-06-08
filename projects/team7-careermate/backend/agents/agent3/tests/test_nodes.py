"""gap_analysis / roadmap_plan 노드 (키 없음 폴백 경로)."""

from __future__ import annotations

import asyncio

from agents.agent3.gap_analysis_agent import run_gap_analysis
from agents.agent3.models import JobRequirement, SkillStatus, SourceOrigin
from agents.agent3.roadmap_plan_agent import run_roadmap_plan
from agents.agent3.state import Agent3State


def _run(coro):
    return asyncio.run(coro)


# ── gap_analysis ──────────────────────────────────────────────
def test_gap_known_skills(profile_frontend, job_frontend):
    st = Agent3State(profile=profile_frontend, job_requirement=job_frontend, weekly_hours=8)
    st = _run(run_gap_analysis(st))
    ga = st.gap_analysis
    assert ga.gaps
    known = [g for g in ga.gaps if g.skill_status == SkillStatus.known]
    assert known and all(g.verified for g in known)
    assert ga.needs_rerun is False  # strong evidence
    # 선행 스킬도 캐시됨 (React 선행 JavaScript/HTML·CSS)
    assert "JavaScript" in st.skill_records or "HTML/CSS" in st.skill_records
    assert st.trace[-1].node == "gap_analysis"


def test_gap_needs_rerun_on_weak(profile_frontend):
    job = JobRequirement(required_skills=["React"], keywords=["React"], evidence_strength="weak")
    st = Agent3State(profile=profile_frontend, job_requirement=job, weekly_hours=8, rerun_count=0)
    st = _run(run_gap_analysis(st))
    assert st.needs_rerun is True
    assert st.trace[-1].decision == "rerun_job"


def test_gap_no_rerun_when_exhausted(profile_frontend):
    job = JobRequirement(required_skills=["React"], keywords=["React"], evidence_strength="weak")
    st = Agent3State(profile=profile_frontend, job_requirement=job, weekly_hours=8, rerun_count=1)
    st = _run(run_gap_analysis(st))
    assert st.needs_rerun is False  # rerun_count >= MAX_RERUN


def test_gap_derives_strong_when_evidence_absent(profile_frontend):
    # evidence_strength 미제공 + 충분한 근거(필수+키워드 다수) → strong 추론 → 재요청 없음
    job = JobRequirement(
        required_skills=["React 구현", "TypeScript"],
        keywords=["React", "TypeScript", "상태관리"],
    )  # evidence_strength 없음
    st = Agent3State(profile=profile_frontend, job_requirement=job, weekly_hours=8)
    st = _run(run_gap_analysis(st))
    assert job.evidence_strength is None  # 모델 기본 None
    assert st.gap_analysis.job_evidence_strength.value == "strong"
    assert st.needs_rerun is False


def test_gap_derives_weak_when_evidence_absent_and_sparse(profile_frontend):
    # evidence_strength 미제공 + 근거 거의 없음 → weak 추론 → 재요청
    job = JobRequirement(required_skills=[], keywords=[])  # 빈 응답
    st = Agent3State(profile=profile_frontend, job_requirement=job, weekly_hours=8, rerun_count=0)
    st = _run(run_gap_analysis(st))
    assert st.gap_analysis.job_evidence_strength.value == "weak"
    assert st.needs_rerun is True


def test_gap_unknown_skill_web_enrichment(monkeypatch, profile_frontend):
    """DB-miss 스킬은 web_search로 보강 — 네트워크 대신 stub 사용 (Rust는 스킬DB에 없음)."""
    from agents.agent3.models import SearchHit

    async def fake_web_search(query, k=5):
        return [SearchHit(title="Rust 공식", url="https://doc.rust-lang.org/book/", source="rust-lang.org")]

    monkeypatch.setattr("agents.agent3.tools.web_search", fake_web_search)

    job = JobRequirement(
        required_skills=["Rust로 시스템 프로그래밍"], keywords=["Rust"], evidence_strength="strong"
    )
    st = Agent3State(profile=profile_frontend, job_requirement=job, weekly_hours=8)
    st = _run(run_gap_analysis(st))

    gq = next((g for g in st.gap_analysis.gaps if "rust" in g.skill.lower()), None)
    assert gq is not None
    assert gq.skill_status == SkillStatus.unknown
    rec = st.skill_records[gq.skill]
    assert rec.resources, "web_search 보강 자원이 있어야"
    assert rec.resources[0].origin == SourceOrigin.web
    assert rec.resources[0].verified is True
    assert st.search_count >= 1
    assert st.verified is True  # web 출처라 강등 안 됨


def test_gap_unknown_skill_no_web_lowers_verified(monkeypatch, profile_frontend):
    """검색까지 실패하면 llm 폴백 → state.verified=False."""

    async def empty_web_search(query, k=5):
        return []

    monkeypatch.setattr("agents.agent3.tools.web_search", empty_web_search)

    job = JobRequirement(
        required_skills=["Rust"], keywords=["Rust"], evidence_strength="strong"
    )
    st = Agent3State(profile=profile_frontend, job_requirement=job, weekly_hours=8)
    st = _run(run_gap_analysis(st))
    assert st.verified is False
    assert st.search_degraded is True


# ── roadmap_plan ──────────────────────────────────────────────
def test_roadmap_covers_all_gaps_and_attaches_resources(profile_frontend, job_frontend):
    st = Agent3State(profile=profile_frontend, job_requirement=job_frontend, weekly_hours=8)
    st = _run(run_gap_analysis(st))
    st = _run(run_roadmap_plan(st))
    rm = st.roadmap

    covered = set()
    for w in rm.weeks:
        covered.update(w.covered_skills)
    for g in st.gap_analysis.gaps:
        assert g.skill in covered

    # known task에는 검증 자원이 부착돼야 한다
    for w in rm.weeks:
        for t in w.tasks:
            rec = st.skill_records.get(t.skill)
            if rec and rec.status == SkillStatus.known:
                assert t.resources, f"{t.skill} 자원 비어있음"

    assert [t.node for t in st.trace] == ["gap_analysis", "roadmap_plan"]


def test_roadmap_empty_when_no_gaps(profile_frontend, job_frontend):
    st = Agent3State(profile=profile_frontend, job_requirement=job_frontend, weekly_hours=8)
    st = _run(run_gap_analysis(st))
    st.gap_analysis.gaps = []
    st = _run(run_roadmap_plan(st))
    assert st.roadmap.weeks == []
