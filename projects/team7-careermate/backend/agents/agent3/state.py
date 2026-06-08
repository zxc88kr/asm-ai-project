"""Agent3 공유 상태 + trace 헬퍼.

LangGraph의 단일 공유 State를 모방한다. gap_analysis → roadmap_plan →
roadmap_critic → finalize 노드가 이 객체를 읽고 일부 필드만 쓴다.
설계 근거: docs/06-data-model.md §1 (CareerMateState).

Agent3 범위 밖(triage/clarify 등)은 제외하고, 에이전트1·2 출력을 입력으로 받는다.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from .models import (
    CriticReport,
    EpisodicMemory,
    FinalOutput,
    GapAnalysis,
    JobRequirement,
    ProfileDiagnosis,
    Roadmap,
    SearchHit,
    SkillRecord,
    TraceEntry,
)


class Agent3State(BaseModel):
    """gap_analysis·roadmap_plan·roadmap_critic·finalize가 공유하는 상태."""

    # ── 입력 (에이전트1·2 출력 + 온보딩) ──────────────────────
    profile: ProfileDiagnosis
    job_requirement: JobRequirement
    weekly_hours: int
    episodic_memory: Optional[EpisodicMemory] = None

    # ── progress_reconciliation 결과(이월/완료 컨텍스트) ──────
    carry_over_skills: list[str] = Field(default_factory=list)
    completed_skills: list[str] = Field(default_factory=list)

    # ── 에이전트 출력 ─────────────────────────────────────────
    gap_analysis: Optional[GapAnalysis] = None
    roadmap: Optional[Roadmap] = None
    critic_report: Optional[CriticReport] = None

    # ── 되먹임/재생성 제어 ────────────────────────────────────
    needs_rerun: bool = False
    rerun_reason: Optional[str] = None
    rerun_count: int = 0          # MAX_RERUN = 1
    revision_count: int = 0       # MAX_REVISIONS = 2

    # ── 웹검색 ────────────────────────────────────────────────
    search_results: dict[str, list[SearchHit]] = Field(default_factory=dict)
    search_count: int = 0
    search_degraded: bool = False

    # ── 툴 캐시 — gap에서 확보한 SkillRecord를 roadmap_plan과 공유 ──
    skill_records: dict[str, SkillRecord] = Field(default_factory=dict)

    # ── 횡단 관심사 ───────────────────────────────────────────
    verified: bool = True
    trace: list[TraceEntry] = Field(default_factory=list)
    final_output: Optional[FinalOutput] = None
    error: Optional[str] = None


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_trace(
    state: Agent3State,
    node: str,
    *,
    input_summary: str = "",
    decision: Optional[str] = None,
    tool_called: Optional[str] = None,
    output_summary: str = "",
) -> None:
    """노드 종료 시 trace에 1건 append (append-only, 기존 항목 수정 금지)."""
    state.trace.append(
        TraceEntry(
            node=node,
            input_summary=input_summary,
            decision=decision,
            tool_called=tool_called,
            output_summary=output_summary,
            ts=now_iso(),
        )
    )
