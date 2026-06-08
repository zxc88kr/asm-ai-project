"""Agent3 LLM 추론 — gap 추출 & 로드맵 생성 (Upstage Solar).

agent2와 동일하게 OpenAI 호환 클라이언트로 Upstage Solar를 호출한다.
환경변수:
  - UPSTAGE_API_KEY      (없으면 규칙기반 폴백으로 동작)
  - UPSTAGE_BASE_URL     (기본 https://api.upstage.ai/v1)
  - UPSTAGE_SOLAR_MODEL  (기본 solar-pro3)

설계 원칙(docs/03-agent-contracts.md):
  - 이 모듈은 **순수 LLM 추론**만 담당. 툴 호출(lookup_skill/web_search)은 노드가 수행.
  - **절대 throw 금지** — LLM 실패/키 없음 시 규칙기반 폴백 반환.
  - 스킬명 추출은 gap 추출 LLM 호출에 통합(추가 호출 0). keywords를 힌트로 제공.
"""

from __future__ import annotations

import json
import math
import os
import re
from collections import Counter
from pathlib import Path
from typing import Optional


def _load_env() -> None:
    """환경변수를 .env에서 로드한다(이미 설정된 값은 유지, override=False).

    탐색 순서:
      1) CWD 기준 .env (uvicorn을 backend/에서 띄우면 backend/.env)
      2) 이 패키지 상위 경로의 .env (agents/.env, backend/.env)
    도커에선 compose의 env_file로 이미 주입되므로 이 로딩은 보조 수단이다.
    python-dotenv가 없거나 파일이 없어도 조용히 넘어간다(throw 금지).
    """
    try:
        from dotenv import find_dotenv, load_dotenv
    except Exception:
        return
    # 1) CWD 기준 자동 탐색
    found = find_dotenv(usecwd=True)
    if found:
        load_dotenv(found, override=False)
    # 2) 패키지 상위 경로(backend/.env 등) 보조 탐색
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / ".env"
        if candidate.exists():
            load_dotenv(candidate, override=False)
            break


_load_env()

from .constants import MAX_WEEKS, MIN_WEEKS
from .models import (
    ChecklistItem,
    EvidenceStrength,
    GapItem,
    JobRequirement,
    Phase,
    PriorityLevel,
    ProfileDiagnosis,
    ResourceItem,
    Roadmap,
    RoadmapHorizon,
    SkillRecord,
    SkillStatus,
    TaskItem,
    WeekPlan,
)

UPSTAGE_BASE_URL = os.getenv("UPSTAGE_BASE_URL", "https://api.upstage.ai/v1")
DEFAULT_SOLAR_MODEL = os.getenv("UPSTAGE_SOLAR_MODEL", "solar-pro3")
_DEFAULT_UNKNOWN_HOURS = 10  # typical_hours 미상 스킬의 기본 추정 시간


def _get_client():
    """UPSTAGE_API_KEY 있으면 OpenAI 호환 클라이언트 반환, 없으면 None."""
    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        return None
    try:
        from openai import AsyncOpenAI

        return AsyncOpenAI(api_key=api_key, base_url=UPSTAGE_BASE_URL)
    except Exception:
        return None


# ═════════════════════════════════════════════════════════════
# 1. gap 추출 — profile vs job_requirement
# ═════════════════════════════════════════════════════════════
async def extract_gaps(
    profile: ProfileDiagnosis,
    job_requirement: JobRequirement,
    completed_skills: Optional[list[str]] = None,
    carry_over_skills: Optional[list[str]] = None,
) -> list[GapItem]:
    """부족 역량을 표준 스킬명으로 추출한다(LLM, 폴백 포함).

    반환 GapItem은 skill/priority/current_level/target_level만 채운다.
    skill_status·verified는 노드가 lookup_skill로 확정하므로 기본값(unknown/False).
    """
    client = _get_client()
    if client is None:
        return _fallback_gaps(profile, job_requirement, completed_skills)

    try:
        prompt = _build_gap_prompt(
            profile, job_requirement, completed_skills, carry_over_skills
        )
        response = await client.chat.completions.create(
            model=DEFAULT_SOLAR_MODEL,
            messages=[
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        data = _parse_json_object(response.choices[0].message.content or "{}")
        gaps = _gaps_from_data(data)
        return gaps or _fallback_gaps(profile, job_requirement, completed_skills)
    except Exception:
        return _fallback_gaps(profile, job_requirement, completed_skills)


def _build_gap_prompt(
    profile: ProfileDiagnosis,
    job: JobRequirement,
    completed_skills: Optional[list[str]],
    carry_over_skills: Optional[list[str]],
) -> str:
    return f"""
당신은 CareerMate의 Agent3(GapRoadmapAgent) 갭 분석 단계입니다.
사용자의 현재 역량(profile)과 목표 직무 요구역량(job_requirement)을 비교해 부족 역량을 도출하세요.

[현재 역량]
요약: {profile.summary}
보유 스킬(실제 가진 기술): {profile.owned_skills}
정성 강점(스킬명 아님): {profile.strengths}
정성 약점(스킬명 아님): {profile.weaknesses}
목표 직무: {profile.target_role}

[목표 직무 요구역량]
필수: {job.required_skills}
우대: {job.preferred_skills}
요구경험: {job.required_experience}
핵심키워드(스킬명 추출 힌트): {job.keywords}

[이미 완료한 스킬(있으면 갭에서 제외)]: {completed_skills or []}
[이전에 이월된 스킬(있으면 우선 포함)]: {carry_over_skills or []}

규칙:
- 목표 직무 요구역량 중 "보유 스킬"에 없는 기술을 부족 역량(gap)으로 도출하세요.
- skill은 "Python", "React", "FastAPI"처럼 짧은 표준 기술명으로 쓰세요(문장 금지). 요구역량이 문장이면 핵심 기술명을 뽑아내세요.
- priority는 필수역량이면 "high", 우대역량이면 "medium", 그 외 보조면 "low".
- current_level은 사용자의 현재 수준("없음"|"기초"|"중급"), target_level은 직무가 요구하는 수준("기초"|"중급"|"실무").
- "보유 스킬"에 이미 있는 기술은 갭에 넣지 마세요. (정성 강점/약점은 문맥 참고용일 뿐 스킬명이 아닙니다)
- 최대 8개까지. 우선순위 높은 순으로 정렬하세요.
- 아래 JSON만 반환하세요. 마크다운 코드블록 금지.

{{
  "gaps": [
    {{"skill": "string", "priority": "high|medium|low", "current_level": "string", "target_level": "string"}}
  ]
}}
""".strip()


def _gaps_from_data(data: dict) -> list[GapItem]:
    raw_gaps = data.get("gaps")
    if not isinstance(raw_gaps, list):
        return []
    gaps: list[GapItem] = []
    seen: set[str] = set()
    for item in raw_gaps:
        if not isinstance(item, dict):
            continue
        skill = str(item.get("skill") or "").strip()
        if not skill or skill.lower() in seen:
            continue
        seen.add(skill.lower())
        gaps.append(
            GapItem(
                skill=skill,
                priority=_coerce_priority(item.get("priority")),
                current_level=str(item.get("current_level") or "없음").strip(),
                target_level=str(item.get("target_level") or "실무").strip(),
            )
        )
    return gaps


def _coerce_priority(value: object) -> PriorityLevel:
    if isinstance(value, str) and value in PriorityLevel._value2member_map_:
        return PriorityLevel(value)
    return PriorityLevel.medium


def _fallback_gaps(
    profile: ProfileDiagnosis,
    job: JobRequirement,
    completed_skills: Optional[list[str]],
) -> list[GapItem]:
    """규칙기반 갭: (필수+우대 키워드) − (보유 스킬 ∪ 완료스킬). 표준 스킬명 추정.

    보유 기준은 profile.owned_skills(실제 스킬). strengths는 정성 개념이라 제외 기준으로 쓰지 않는다.
    """
    from .tools import normalize_skill_name

    completed = {s.lower() for s in (completed_skills or [])}
    owned = {normalize_skill_name(s).lower() for s in profile.owned_skills} | completed

    # 키워드/필수/우대에서 스킬 후보 수집(키워드가 가장 스킬명에 가까움)
    required_norm = {normalize_skill_name(k) for k in job.keywords if k.strip()}
    for sent in job.required_skills + job.preferred_skills:
        required_norm.add(normalize_skill_name(_first_skill_token(sent)))

    high = {normalize_skill_name(k) for k in job.keywords if k.strip()}

    gaps: list[GapItem] = []
    seen: set[str] = set()
    for skill in required_norm:
        if not skill or skill.lower() in owned or skill.lower() in seen:
            continue
        seen.add(skill.lower())
        gaps.append(
            GapItem(
                skill=skill,
                priority=PriorityLevel.high if skill in high else PriorityLevel.medium,
                current_level="없음",
                target_level="실무",
            )
        )
    # 우선순위(high 먼저) 정렬, 최대 8개
    gaps.sort(key=lambda g: 0 if g.priority == PriorityLevel.high else 1)
    return gaps[:8]


def _first_skill_token(sentence: str) -> str:
    """문장형 요구역량에서 맨 앞 기술명 토큰을 대략 추출(폴백용)."""
    token = re.split(r"[으로로 을를 이가 와과,.]", sentence.strip(), maxsplit=1)[0]
    return token.strip() or sentence.strip()


# ═════════════════════════════════════════════════════════════
# 2. 로드맵 생성 — gap + skill_records → 주차별 계획
# ═════════════════════════════════════════════════════════════
def suggest_total_weeks(
    gaps: list[GapItem],
    skill_records: dict[str, SkillRecord],
    weekly_hours: int,
) -> int:
    """갭 총 학습시간 / 주당 가용시간 → 기간 동적 산출(Plan-and-Solve). [MIN,MAX] 캡."""
    weekly = max(1, weekly_hours)
    total_hours = 0
    for g in gaps:
        rec = skill_records.get(g.skill)
        total_hours += rec.typical_hours if rec and rec.typical_hours > 0 else _DEFAULT_UNKNOWN_HOURS
    weeks = math.ceil(total_hours / weekly) if total_hours else MIN_WEEKS
    return max(MIN_WEEKS, min(MAX_WEEKS, weeks))


def _horizon_for(total_weeks: int) -> RoadmapHorizon:
    if total_weeks <= 4:
        return RoadmapHorizon.weeks_4
    if total_weeks <= 6:
        return RoadmapHorizon.weeks_6
    return RoadmapHorizon.weeks_8


async def generate_roadmap(
    gaps: list[GapItem],
    weekly_hours: int,
    skill_records: dict[str, SkillRecord],
    total_weeks: Optional[int] = None,
    revision_context: Optional[dict] = None,
    completed_skills: Optional[list[str]] = None,
    carry_over_skills: Optional[list[str]] = None,
    owned_skills: Optional[list[str]] = None,
) -> Roadmap:
    """주차별 로드맵을 생성한다(LLM, 규칙기반 폴백 포함).

    skill_records: gap 스킬명 → lookup_skill/web_search로 노드가 미리 확보한 SkillRecord.
    owned_skills: 사용자가 이미 보유한 스킬(profile.owned_skills). 재학습 주차를 막는 데 사용.
    LLM은 주차 배치·목표만 생성하고, 자원(resources)은 skill_records에서 결정론적으로 부착해
    환각 링크를 차단한다.
    """
    if total_weeks is None:
        total_weeks = suggest_total_weeks(gaps, skill_records, weekly_hours)

    client = _get_client()
    if client is None:
        return _fallback_roadmap(gaps, weekly_hours, skill_records, total_weeks)

    # 이미 보유/완료한 스킬은 재학습 대상에서 제외하도록 합쳐 전달
    known_skills = list(dict.fromkeys((owned_skills or []) + (completed_skills or [])))

    try:
        prompt = _build_roadmap_prompt(
            gaps, weekly_hours, skill_records, total_weeks,
            revision_context, carry_over_skills, known_skills,
        )
        response = await client.chat.completions.create(
            model=DEFAULT_SOLAR_MODEL,
            messages=[
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        data = _parse_json_object(response.choices[0].message.content or "{}")
        roadmap = _roadmap_from_data(data, weekly_hours, skill_records)
        if not roadmap.weeks:
            return _fallback_roadmap(gaps, weekly_hours, skill_records, total_weeks)
        roadmap.phases = build_phases(roadmap.weeks)
        return roadmap
    except Exception:
        return _fallback_roadmap(gaps, weekly_hours, skill_records, total_weeks)


def _build_roadmap_prompt(
    gaps: list[GapItem],
    weekly_hours: int,
    skill_records: dict[str, SkillRecord],
    total_weeks: int,
    revision_context: Optional[dict],
    carry_over_skills: Optional[list[str]],
    known_skills: Optional[list[str]] = None,
) -> str:
    skill_lines = []
    for g in gaps:
        rec = skill_records.get(g.skill)
        prereqs = rec.prereqs if rec else []
        hours = rec.typical_hours if rec and rec.typical_hours > 0 else _DEFAULT_UNKNOWN_HOURS
        skill_lines.append(f"- {g.skill} (우선순위 {g.priority.value}, 선행 {prereqs}, 표준 {hours}h)")
    skills_block = "\n".join(skill_lines)

    revision_block = ""
    if revision_context and revision_context.get("violations"):
        revision_block = (
            "\n[이전 생성 위반 사항 — 반드시 수정]\n"
            + "\n".join(f"- {v}" for v in revision_context["violations"])
        )

    return f"""
당신은 CareerMate의 Agent3 로드맵 생성 단계입니다.
부족 역량을 주당 가용시간 안에서 선후행 순서대로 배치한 주차별 학습 로드맵을 만드세요.

[부족 역량(우선순위·선행·표준시간)]
{skills_block}

[이미 보유한 스킬 — 재학습 금지]: {known_skills or []}

[제약]
- 주당 가용시간: {weekly_hours}시간. 각 주차 planned_hours는 절대 이 값을 넘기지 마세요.
- 총 주차 수: 약 {total_weeks}주를 목표로 하되 갭을 모두 담으세요.
- 선행 스킬은 반드시 후행 스킬보다 앞 주차에 배치하세요(예: Python을 FastAPI보다 먼저).
- 모든 부족 역량이 최소 한 주차에 covered_skills로 포함돼야 합니다.
- "합격 보장", "반드시 취업" 같은 단정 표현을 절대 쓰지 마세요.
- 이월 스킬(있으면 우선): {carry_over_skills or []}
{revision_block}

[보유 스킬 처리]
- "이미 보유한 스킬"은 새로 배우는 학습 주차로 만들지 마세요. 주차는 부족 역량 학습에 집중하세요.
- 선행으로 꼭 필요하면 1주차에 "짧은 복습"으로만 가볍게 언급하고, 주차 대부분을 부족 역량에 쓰세요.

[단계(phase) 구성]
- 전체를 정확히 4개 단계로 나누세요. 각 단계의 주차 수를 최대한 균등하게(±1주) 배분하세요.
- 각 단계는 3~4개의 task(체크리스트 항목)를 갖게 하세요.
- 단계 제목과 그 단계의 실제 내용이 일치해야 합니다(예: "프로젝트 실전" 단계에는 학습이 아닌 프로젝트성 task를 넣으세요).
- 단계명 예시 순서: "기초 다지기" → "핵심 역량 강화" → "프로젝트 실전" → "포트폴리오 & 준비".

규칙:
- 각 task의 est_hours 합이 그 주차 planned_hours가 되도록 하세요.
- resources(링크)는 넣지 마세요. 시스템이 검증된 자원을 자동 부착합니다.
- 연속된 주차가 같은 phase(단계명)를 공유해 묶이도록 각 주차에 phase를 붙이세요.
- 아래 JSON만 반환하세요. 마크다운 코드블록 금지.

{{
  "rationale": "기간 산출 근거 한국어 1-2문장",
  "weeks": [
    {{
      "week_index": 1,
      "phase": "기초 다지기",
      "objectives": ["string"],
      "planned_hours": {weekly_hours},
      "tasks": [{{"title": "string", "skill": "string", "est_hours": 4}}]
    }}
  ]
}}
""".strip()


def _roadmap_from_data(
    data: dict,
    weekly_hours: int,
    skill_records: dict[str, SkillRecord],
) -> Roadmap:
    raw_weeks = data.get("weeks")
    if not isinstance(raw_weeks, list):
        return Roadmap(weekly_hours_budget=weekly_hours)

    weeks: list[WeekPlan] = []
    for i, w in enumerate(raw_weeks, start=1):
        if not isinstance(w, dict):
            continue
        tasks: list[TaskItem] = []
        covered: list[str] = []
        for t in w.get("tasks", []) or []:
            if not isinstance(t, dict):
                continue
            skill = str(t.get("skill") or "").strip()
            rec = skill_records.get(skill)
            resources = list(rec.resources) if rec else []
            verified = bool(rec.verified) if rec else False
            tasks.append(
                TaskItem(
                    title=str(t.get("title") or skill).strip(),
                    skill=skill,
                    resources=resources,
                    est_hours=_safe_int(t.get("est_hours")),
                    verified=verified,
                )
            )
            if skill and skill not in covered:
                covered.append(skill)
        planned = _safe_int(w.get("planned_hours")) or sum(t.est_hours for t in tasks)
        phase = w.get("phase")
        weeks.append(
            WeekPlan(
                week_index=_safe_int(w.get("week_index")) or i,
                objectives=[str(o).strip() for o in (w.get("objectives") or []) if str(o).strip()],
                tasks=tasks,
                covered_skills=covered,
                planned_hours=planned,
                phase=str(phase).strip() if phase else None,
            )
        )

    total_weeks = len(weeks)
    return Roadmap(
        horizon=_horizon_for(total_weeks),
        total_weeks=total_weeks,
        weeks=weeks,
        weekly_hours_budget=weekly_hours,
        rationale=str(data.get("rationale") or "").strip(),
    )


# ─────────────────────────────────────────────────────────────
# 규칙기반 폴백 패커 — critic 4종을 구조적으로 만족
# ─────────────────────────────────────────────────────────────
def _fallback_roadmap(
    gaps: list[GapItem],
    weekly_hours: int,
    skill_records: dict[str, SkillRecord],
    total_weeks: int,
) -> Roadmap:
    """선후행 토폴로지 순서로 스킬을 주당 시간 예산 안에 그리디 배치한다.

    보장: 각 주차 planned_hours ≤ weekly_hours(②), 선행이 후행보다 앞(③),
          모든 갭이 covered(①), 금칙 표현 없음(④).
    """
    weekly = max(1, weekly_hours)
    order = _topo_order_gaps(gaps, skill_records)

    weeks: list[WeekPlan] = []
    cur_idx = 1
    cur_hours = 0
    cur_tasks: list[TaskItem] = []
    cur_skills: list[str] = []

    def close_week():
        nonlocal cur_idx, cur_hours, cur_tasks, cur_skills
        if cur_tasks:
            weeks.append(
                WeekPlan(
                    week_index=cur_idx,
                    objectives=[f"{s} 학습" for s in cur_skills],
                    tasks=cur_tasks,
                    covered_skills=list(cur_skills),
                    planned_hours=cur_hours,
                )
            )
            cur_idx += 1
            cur_hours = 0
            cur_tasks = []
            cur_skills = []

    total_hours = 0
    for skill in order:
        rec = skill_records.get(skill)
        hours = rec.typical_hours if rec and rec.typical_hours > 0 else _DEFAULT_UNKNOWN_HOURS
        total_hours += hours
        resources = list(rec.resources) if rec else []
        verified = bool(rec.verified) if rec else False

        remaining = hours
        chunk_no = 0
        while remaining > 0:
            avail = weekly - cur_hours
            if avail <= 0:
                close_week()
                avail = weekly
            take = min(remaining, avail)
            chunk_no += 1
            title = skill if hours <= weekly else f"{skill} (파트 {chunk_no})"
            cur_tasks.append(
                TaskItem(
                    title=title,
                    skill=skill,
                    resources=resources,
                    est_hours=take,
                    verified=verified,
                )
            )
            if skill not in cur_skills:
                cur_skills.append(skill)
            cur_hours += take
            remaining -= take
            if cur_hours >= weekly:
                close_week()
    close_week()

    n_weeks = len(weeks)
    return Roadmap(
        horizon=_horizon_for(n_weeks),
        total_weeks=n_weeks,
        weeks=weeks,
        phases=build_phases(weeks),
        weekly_hours_budget=weekly,
        rationale=(
            f"갭 {len(gaps)}개·총 {total_hours}h·주 {weekly}h 기준 선후행 순서로 "
            f"{n_weeks}주에 배치했습니다."
        ),
    )


# ─────────────────────────────────────────────────────────────
# 단계(Phase) 빌더 — weeks를 항상 정확히 4개 카드로 균등 분할
# ─────────────────────────────────────────────────────────────
TARGET_PHASES = 4  # UI 로드맵 카드 수 고정
_DEFAULT_PHASE_TITLES = ["기초 다지기", "핵심 역량 강화", "프로젝트 실전", "포트폴리오 & 준비"]


def build_phases(weeks: list[WeekPlan], target: int = TARGET_PHASES) -> list[Phase]:
    """주차들을 **정확히 `target`개**(주차가 더 적으면 주차 수만큼) 단계로 균등 분할한다.

    화면의 "4카드 × 균등 주차" 레이아웃을 보장한다(예: 8주 → 2·2·2·2).
    제목은 그 그룹 주차의 LLM phase 라벨(최빈, 중복 아닌 경우)을 쓰고,
    없거나 충돌하면 표준 4단계 제목(_DEFAULT_PHASE_TITLES)을 위치별로 부여한다.
    각 단계 items는 그룹 주차의 task를 ChecklistItem(id 부여, completed 없음)으로 변환한다.
    """
    if not weeks:
        return []
    ordered = sorted(weeks, key=lambda w: w.week_index)
    k = min(target, len(ordered))
    groups = _even_contiguous_split(ordered, k)

    phases: list[Phase] = []
    used_titles: set[str] = set()
    for idx, ws in enumerate(groups):
        title = _pick_phase_title(ws, idx, used_titles)
        used_titles.add(title)
        items: list[ChecklistItem] = []
        n = 1
        for w in ws:
            for t in w.tasks:
                items.append(
                    ChecklistItem(
                        id=f"p{idx + 1}-i{n}",
                        label=t.title,
                        skill=t.skill,
                        resources=list(t.resources),
                        est_hours=t.est_hours,
                    )
                )
                n += 1
        phases.append(
            Phase(
                index=idx + 1,
                title=title,
                week_from=ws[0].week_index,
                week_to=ws[-1].week_index,
                items=items,
            )
        )
    return phases


def _even_contiguous_split(seq: list, k: int) -> list[list]:
    """seq를 연속 유지하며 k개로 최대한 균등 분할. 나머지는 앞 그룹부터 +1."""
    n = len(seq)
    base, rem = divmod(n, k)
    out: list[list] = []
    i = 0
    for g in range(k):
        size = base + (1 if g < rem else 0)
        out.append(seq[i : i + size])
        i += size
    return out


def _pick_phase_title(ws: list[WeekPlan], idx: int, used: set[str]) -> str:
    """그룹 제목: LLM 라벨 최빈값(중복 아니면) 우선, 없으면 표준 제목."""
    labels = [(w.phase or "").strip() for w in ws if (w.phase or "").strip()]
    if labels:
        common = Counter(labels).most_common(1)[0][0]
        if common and common not in used:
            return common
    if idx < len(_DEFAULT_PHASE_TITLES) and _DEFAULT_PHASE_TITLES[idx] not in used:
        return _DEFAULT_PHASE_TITLES[idx]
    return f"{idx + 1}단계"


def _topo_order_gaps(
    gaps: list[GapItem],
    skill_records: dict[str, SkillRecord],
) -> list[str]:
    """갭 스킬을 선후행(prereq) 위상정렬. 같은 레벨은 high 우선순위 먼저.

    갭 집합 내부의 prereq만 선행 제약으로 고려한다(갭이 아닌 prereq는 무시).
    사이클이 있어도(이론상 DB는 DAG) 남은 노드를 우선순위 순으로 덧붙여 누락 방지.
    """
    gap_skills = [g.skill for g in gaps]
    gap_set = set(gap_skills)
    priority_rank = {
        g.skill: (0 if g.priority == PriorityLevel.high else 1 if g.priority == PriorityLevel.medium else 2)
        for g in gaps
    }

    # 갭 내부 prereq만 남긴 인접/진입차수
    deps: dict[str, set[str]] = {}
    for skill in gap_skills:
        rec = skill_records.get(skill)
        prereqs = set(rec.prereqs) & gap_set if rec else set()
        prereqs.discard(skill)
        deps[skill] = prereqs

    ordered: list[str] = []
    placed: set[str] = set()
    # 반복적으로 "선행이 모두 배치된" 스킬 중 우선순위 높은 것부터 배치
    remaining = list(gap_skills)
    while remaining:
        ready = [s for s in remaining if deps[s] <= placed]
        if not ready:
            # 사이클/외부의존 등 — 남은 것 우선순위 순으로 강제 배치(누락 방지)
            ready = sorted(remaining, key=lambda s: priority_rank.get(s, 1))[:1]
        ready.sort(key=lambda s: priority_rank.get(s, 1))
        nxt = ready[0]
        ordered.append(nxt)
        placed.add(nxt)
        remaining.remove(nxt)
    return ordered


# ─────────────────────────────────────────────────────────────
# 공통 파싱 헬퍼 (agent2 패턴 재사용)
# ─────────────────────────────────────────────────────────────
def _parse_json_object(content: str) -> dict:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?", "", content).strip()
        content = re.sub(r"```$", "", content).strip()
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        content = match.group(0)
    return json.loads(content)


def _safe_int(value: object) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0
