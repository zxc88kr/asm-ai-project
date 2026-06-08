"""Agent3 래퍼(Agent3.default) — 백엔드 호출 형태 검증 (오프라인 폴백)."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

from agents.agent3.Agent3 import Agent3, _parse_weekly_hours


def _run(coro):
    return asyncio.run(coro)


def _request(**kw):
    base = dict(
        majorAndYear="컴퓨터공학과 4학년",
        currentStatus="재학생",
        interests=["프론트엔드 개발"],
        ownedSkills=["HTML/CSS", "JavaScript"],
        targetJob="프론트엔드 엔지니어",
        preferredCompanyType="스타트업",
        availableTime="주 15시간",
        concerns=["포트폴리오 고민"],
    )
    base.update(kw)
    return SimpleNamespace(**base)


def test_parse_weekly_hours():
    assert _parse_weekly_hours("주 15시간") == 15
    assert _parse_weekly_hours("20시간 이상") == 20
    assert _parse_weekly_hours("15") == 15
    assert _parse_weekly_hours(8) == 8
    assert _parse_weekly_hours(None) == 10
    assert _parse_weekly_hours("미정") == 10


def test_agent3_wrapper_output_shape():
    req = _request()
    a1 = {"summary": "프론트 지망 4학년", "strengths": ["전공 일치도"], "weaknesses": ["경험 부족"], "evidence": {}}
    a2 = {
        "required_skills": ["React로 화면 구현", "TypeScript 타입 안전"],
        "preferred_skills": ["상태관리"],
        "required_experience": [],
        "keywords": ["React", "TypeScript", "상태관리"],
    }
    result = _run(Agent3().default(req, a1, a2))

    # 최상위 키
    assert set(result) == {"recommendedPath", "skillGaps", "roadmap"}
    assert "프론트엔드 엔지니어" in result["recommendedPath"]

    # roadmap 4버킷 모두 리스트
    rm = result["roadmap"]
    assert set(rm) == {"week1To2", "week3To4", "week5To6", "week7To8"}
    assert all(isinstance(rm[k], list) for k in rm)

    # skillGaps 문장형
    assert result["skillGaps"]
    assert all("학습이 필요" in s for s in result["skillGaps"])

    # 갭에 직무 핵심 스킬이 들어감
    gaps_text = " ".join(result["skillGaps"])
    assert "React" in gaps_text


def test_agent3_wrapper_empty_job():
    # 빈 job → 갭 없음 → 빈 로드맵 버킷 (크래시 없음)
    req = _request()
    result = _run(Agent3().default(req, {}, {"required_skills": [], "keywords": []}))
    assert set(result["roadmap"]) == {"week1To2", "week3To4", "week5To6", "week7To8"}
