"""gap_analysis 노드 — profile vs job_requirement 비교로 부족 역량 도출.

흐름(ReAct: Reason → Act → Observe):
  1. (LLM) extract_gaps로 부족 역량을 표준 스킬명으로 추출 (keywords 힌트).
  2. (Act) 각 갭에 normalize_skill_name + lookup_skill → skill_status/verified 확정.
  3. (Act) status=unknown이면 web_search로 실제 url 보강(예산 가드). 성공=web origin,
     실패=llm origin(state.verified=False로 강등).
  4. 갭 스킬의 선행(prereq) SkillRecord도 미리 확보해 roadmap_plan과 공유.
  5. job_requirement.evidence_strength=weak이고 rerun_count<MAX_RERUN이면 needs_rerun=True.
     (rerun_count 증가는 conditional edge/orchestrator가 담당 — CANON E)
  6. GapAnalysis 조립 + TraceEntry 기록.

설계 근거: docs/02-agent-graph.md §4, docs/03-agent-contracts.md §4.
**throw 금지** — 모든 외부 호출은 폴백을 가진다.
"""

from __future__ import annotations

from .constants import MAX_RERUN
from .llm import extract_gaps
from .models import (
    EvidenceStrength,
    GapAnalysis,
    GapItem,
    ResourceItem,
    SkillRecord,
    SkillStatus,
    SourceOrigin,
)
from .state import Agent3State, append_trace
from .tools import lookup_skill, normalize_skill_name, web_search_budgeted

_RESOURCE_SEARCH_K = 3


async def run_gap_analysis(state: Agent3State) -> Agent3State:
    """gap_analysis 노드 본문. state를 갱신해 반환한다."""
    job = state.job_requirement

    # 1. (LLM) 부족 역량 추출
    gaps = await extract_gaps(
        state.profile,
        job,
        completed_skills=state.completed_skills,
        carry_over_skills=state.carry_over_skills,
    )

    # 2~3. 각 갭에 툴 적용 (lookup_skill → 필요 시 web_search)
    used_web = False
    enriched: list[GapItem] = []
    for g in gaps:
        norm = normalize_skill_name(g.skill)
        g.skill = norm
        record = lookup_skill(norm)

        if record.status == SkillStatus.known:
            g.skill_status = SkillStatus.known
            g.verified = True
            state.skill_records[norm] = record
        else:
            g.skill_status = SkillStatus.unknown
            g.verified = False  # GapItem.verified = DB-known 여부 (docs §2-5)
            record = await _enrich_unknown_skill(state, norm)
            state.skill_records[norm] = record
            if record.resources:
                used_web = True
        enriched.append(g)

    # 4. 갭 스킬의 선행(prereq)도 미리 확보 (roadmap_plan의 선행 주차 자원용)
    for g in enriched:
        rec = state.skill_records.get(g.skill)
        for prereq in (rec.prereqs if rec else []):
            if prereq not in state.skill_records:
                state.skill_records[prereq] = lookup_skill(prereq)

    # 5. 되먹임 판단 (evidence_strength=weak → Job 재요청)
    #    에이전트2가 evidence_strength를 주지 않으면(None) job_requirement 충실도로 추론한다.
    effective_strength = _effective_evidence_strength(job)
    needs_rerun = False
    rerun_reason = None
    if effective_strength == EvidenceStrength.weak and state.rerun_count < MAX_RERUN:
        needs_rerun = True
        rerun_reason = (
            "job_requirement 근거 약함(필수역량·키워드 부족) → 필수역량 재추출 필요"
        )

    # 6. GapAnalysis 조립
    gap_analysis = GapAnalysis(
        gaps=enriched,
        job_evidence_strength=effective_strength,
        needs_rerun=needs_rerun,
        rerun_reason=rerun_reason,
    )
    state.gap_analysis = gap_analysis
    state.needs_rerun = needs_rerun
    state.rerun_reason = rerun_reason

    # 7. trace
    tool_called = "lookup_skill"
    if used_web:
        tool_called = "lookup_skill+web_search"
    gap_summary = ", ".join(f"{g.skill}({g.priority.value})" for g in enriched) or "없음"
    append_trace(
        state,
        "gap_analysis",
        input_summary=(
            f"보유 {len(state.profile.owned_skills)}개 vs 필수 {len(job.required_skills)}개, "
            f"evidence={effective_strength.value}"
            + ("(추론)" if job.evidence_strength is None else "")
        ),
        decision="rerun_job" if needs_rerun else "skip_rerun",
        tool_called=tool_called,
        output_summary=(
            f"gaps=[{gap_summary}], needs_rerun={needs_rerun}, "
            f"verified={state.verified}, search_count={state.search_count}"
        ),
    )
    return state


def _effective_evidence_strength(job) -> EvidenceStrength:
    """job_requirement의 근거 강도를 결정한다.

    에이전트2가 evidence_strength를 명시하면 그 값을 쓰고, 주지 않으면(None) 추론한다.
    추론 규칙: 필수역량 + 키워드 신호가 2개 미만이면 근거 부실(weak), 그 외 strong.
    (Agent2가 보통 여러 역량을 반환하므로 대부분 strong → 불필요한 재요청 없음.
     거의 빈 응답일 때만 weak로 잡아 재요청 가치를 살린다.)
    """
    if job.evidence_strength is not None:
        return job.evidence_strength
    signal = len(job.required_skills) + len(job.keywords)
    return EvidenceStrength.weak if signal < 2 else EvidenceStrength.strong


async def _enrich_unknown_skill(state: Agent3State, skill: str) -> SkillRecord:
    """DB-miss 스킬을 web_search로 보강한다.

    성공: ResourceItem(origin=web, verified=True) 채운 SkillRecord 반환.
    실패: 빈 resources + state.verified=False (llm origin 폴백).
    typical_hours는 알 수 없으므로 0 유지(패커가 기본 추정시간 사용).
    """
    query = f"{skill} 학습 강의 튜토리얼 공식문서"
    hits, new_count, degraded = await web_search_budgeted(
        query, state.search_results, state.search_count, k=_RESOURCE_SEARCH_K
    )
    state.search_count = new_count
    if degraded:
        state.search_degraded = True

    if hits:
        resources = [
            ResourceItem(
                title=h.title,
                url=h.url,
                type="doc",
                verified=True,
                origin=SourceOrigin.web,
                source_url=h.url,
            )
            for h in hits
        ]
        return SkillRecord(
            name=skill,
            status=SkillStatus.unknown,  # DB엔 여전히 unknown
            prereqs=[],
            resources=resources,
            typical_hours=0,
            verified=True,  # web 출처라 자원 자체는 검증됨
        )

    # 검색까지 실패 → 순수 LLM 폴백, 전역 verified 강등
    state.verified = False
    return SkillRecord(
        name=skill,
        status=SkillStatus.unknown,
        prereqs=[],
        resources=[],
        typical_hours=0,
        verified=False,
    )
