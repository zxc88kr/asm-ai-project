"""roadmap_plan 노드 — 갭을 주차별 학습 로드맵으로 변환 (Agent3 핵심).

흐름:
  1. gap_analysis.gaps + state.skill_records(갭+선행, 6단계가 확보)를 입력으로.
  2. suggest_total_weeks로 기간 동적 산출(Plan-and-Solve).
  3. critic_report가 revise면 위반 사유를 revision_context로 주입(재생성).
  4. (LLM) generate_roadmap 호출 — 주차 배치·목표 생성, 자원은 skill_records에서 부착.
  5. 후처리: LLM이 추가한 스킬(선행 주차 등)의 스킬명 정규화 + lookup_skill로 자원 보강,
     covered_skills 재계산, verified 전파(미검증 자원 혼입 시 state.verified=False).
  6. state.roadmap 기록 + TraceEntry.

설계 근거: docs/02-agent-graph.md §4, docs/06-data-model.md §2-6.
**throw 금지** — generate_roadmap이 규칙기반 폴백을 내장.
"""

from __future__ import annotations

from typing import Optional

from .llm import build_phases, generate_roadmap, suggest_total_weeks
from .models import CriticVerdict, Roadmap
from .state import Agent3State, append_trace
from .tools import lookup_skill, normalize_skill_name


async def run_roadmap_plan(state: Agent3State) -> Agent3State:
    """roadmap_plan 노드 본문. async 그래프와의 호출 균일성을 위해 동기로 둔다
    (내부 LLM 호출은 동기 OpenAI 클라이언트, web_search는 호출하지 않음 —
     갭 스킬 자원은 6단계 gap_analysis가 이미 확보)."""
    gap_analysis = state.gap_analysis
    gaps = gap_analysis.gaps if gap_analysis else []

    # 갭이 없으면 빈 로드맵 (정상 — 사용자가 이미 자격 충족)
    if not gaps:
        state.roadmap = Roadmap(weekly_hours_budget=state.weekly_hours, rationale="부족 역량이 없어 추가 로드맵이 필요하지 않습니다.")
        append_trace(
            state,
            "roadmap_plan",
            input_summary="gaps=0",
            output_summary="갭 없음 → 빈 로드맵",
        )
        return state

    # 2. 기간 동적 산출
    total_weeks = suggest_total_weeks(gaps, state.skill_records, state.weekly_hours)

    # 3. revise 재생성 컨텍스트
    revision_context = _build_revision_context(state)

    # 4. (LLM) 로드맵 생성
    roadmap = await generate_roadmap(
        gaps,
        state.weekly_hours,
        state.skill_records,
        total_weeks=total_weeks,
        revision_context=revision_context,
        completed_skills=state.completed_skills,
        carry_over_skills=state.carry_over_skills,
        owned_skills=state.profile.owned_skills,
    ) # 비동기로 수정을 진행하였습니다.

    # 5. 후처리: LLM 추가 스킬 자원 보강 + verified 전파
    _post_process(state, roadmap)
    # 후처리로 task 스킬·자원이 바뀌므로 단계(phase)를 최종 task 기준으로 재빌드
    roadmap.phases = build_phases(roadmap.weeks)
    state.roadmap = roadmap

    # 6. trace
    rev = state.revision_count
    append_trace(
        state,
        "roadmap_plan",
        input_summary=(
            f"gaps={len(gaps)}, weekly_hours={state.weekly_hours}, "
            f"total_weeks={total_weeks}, revision={rev}"
            + (", revise 반영" if revision_context else "")
        ),
        tool_called="lookup_skill",
        output_summary=(
            f"horizon={roadmap.horizon.value}, weeks={roadmap.total_weeks}, "
            f"verified={state.verified}"
        ),
    )
    return state


def _build_revision_context(state: Agent3State) -> Optional[dict]:
    """critic_report가 revise면 위반 사유를 LLM 재생성용 컨텍스트로 변환."""
    report = state.critic_report
    if report is None or report.verdict != CriticVerdict.revise or not report.violations:
        return None
    violations = [
        f"{v.type.value} @ {v.location}: {v.detail}" for v in report.violations
    ]
    return {"violations": violations, "revision_count": state.revision_count}


def _post_process(state: Agent3State, roadmap: Roadmap) -> None:
    """LLM이 만든 로드맵을 정규화·보강하고 verified를 전파한다.

    - task.skill 정규화(normalize_skill_name) 후 skill_records에 없으면 lookup_skill로 확보.
    - 자원이 빈 task에 record 자원을 부착(환각 링크 차단: lookup_skill 유래만).
    - covered_skills를 정규화된 task 스킬로 재계산.
    - 검증되지 않은 자원(원천 url 없음)이 섞이면 state.verified=False로 강등(절대 올리지 않음).
      단, 스킬이 없는 활동성 항목(예: "포트폴리오 정리", "면접 준비")은 자원이 없어도
      전역 verified를 깎지 않는다(환각이 아니라 의도된 활동이므로).
    """
    all_verified = True
    for week in roadmap.weeks:
        for task in week.tasks:
            norm = normalize_skill_name(task.skill)
            task.skill = norm

            record = state.skill_records.get(norm)
            if record is None:
                record = lookup_skill(norm)  # 저비용(네트워크 없음); 결과 캐시
                state.skill_records[norm] = record

            if not task.resources and record.resources:
                task.resources = list(record.resources)

            task.verified = bool(task.resources) and all(r.verified for r in task.resources)
            # 스킬 있는 항목이 검증 자원을 못 얻으면 llm-origin → 전역 강등.
            # 스킬 없는 활동성 항목은 자원이 없어도 정상이므로 강등하지 않음.
            if task.skill and not task.verified:
                all_verified = False

        # covered_skills를 정규화 결과로 재계산(중복 제거, 순서 유지)
        week.covered_skills = list(dict.fromkeys(t.skill for t in week.tasks))

    # verified는 내리기만 한다(gap 단계에서 이미 내렸을 수 있음)
    state.verified = state.verified and all_verified
