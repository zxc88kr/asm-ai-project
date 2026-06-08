"""tools.py — lookup_skill / normalize_skill_name / list_skills_for_role / web_search 예산."""

from __future__ import annotations

import asyncio

from agents.agent3.models import SkillStatus, SourceOrigin
from agents.agent3.tools import (
    list_skills_for_role,
    lookup_skill,
    normalize_role_name,
    normalize_skill_name,
    web_search,
    web_search_budgeted,
)


# ── normalize_skill_name ──────────────────────────────────────
def test_normalize_alias_and_case():
    assert normalize_skill_name("react.js") == "React"
    assert normalize_skill_name("fast api") == "FastAPI"
    assert normalize_skill_name("파이썬") == "Python"
    assert normalize_skill_name("PYTHON") == "Python"
    assert normalize_skill_name("  ts  ") == "TypeScript"


def test_normalize_passthrough_on_miss():
    assert normalize_skill_name("React") == "React"
    assert normalize_skill_name("UnknownLib") == "UnknownLib"


def test_normalize_empty():
    assert normalize_skill_name("") == ""


# ── lookup_skill ──────────────────────────────────────────────
def test_lookup_known():
    r = lookup_skill("react.js")
    assert r.status == SkillStatus.known
    assert r.name == "React"
    assert r.verified is True
    assert "JavaScript" in r.prereqs
    assert r.typical_hours == 40
    assert r.resources[0].origin == SourceOrigin.db


def test_lookup_unknown_fallback():
    r = lookup_skill("SomeObscureLib")
    assert r.status == SkillStatus.unknown
    assert r.verified is False
    assert r.resources == [] and r.prereqs == [] and r.typical_hours == 0


def test_lookup_empty_no_throw():
    assert lookup_skill("").status == SkillStatus.unknown


# ── list_skills_for_role ──────────────────────────────────────
def test_list_skills_backend():
    skills = list_skills_for_role("백엔드 개발자")
    names = {s.name for s in skills}
    assert "FastAPI" in names and "PostgreSQL" in names
    assert all(s.status == SkillStatus.known for s in skills)


def test_list_skills_unknown_role():
    assert list_skills_for_role("존재하지 않는 직무") == []


# ── normalize_role_name (직무 별칭 정규화) ────────────────────
def test_normalize_role_alias():
    assert normalize_role_name("프론트엔드 엔지니어") == "프론트엔드 개발자"
    assert normalize_role_name("백엔드 엔지니어") == "백엔드 개발자"
    assert normalize_role_name("ML Engineer") == "머신러닝 엔지니어"
    assert normalize_role_name("데브옵스") == "DevOps 엔지니어"


def test_normalize_role_passthrough():
    assert normalize_role_name("프론트엔드 개발자") == "프론트엔드 개발자"  # 이미 표준
    assert normalize_role_name("희귀직무") == "희귀직무"  # 미매칭 원문


def test_list_skills_via_role_alias():
    # 별칭으로도 직무 스킬이 조회돼야 (프론트엔드 엔지니어 → 프론트엔드 개발자)
    skills = list_skills_for_role("프론트엔드 엔지니어")
    assert len(skills) == 10
    names = {s.name for s in skills}
    assert "React" in names and "TypeScript" in names


def test_new_roles_present():
    for role in ["데이터 분석가", "데이터 엔지니어", "머신러닝 엔지니어", "DevOps 엔지니어", "풀스택 개발자"]:
        assert list_skills_for_role(role), f"{role} 매핑 비어있음"


# ── web_search 예산/캐시 (네트워크 없이) ──────────────────────
def test_web_search_empty_query():
    assert asyncio.run(web_search("")) == []
    assert asyncio.run(web_search("   ")) == []


def test_budget_cache_hit_no_count_increase():
    from agents.agent3.models import SearchHit

    cache = {"q": [SearchHit(title="t", url="https://x.com")]}
    hits, cnt, deg = asyncio.run(web_search_budgeted("q", cache, 3))
    assert cnt == 3 and deg is False and hits[0].url == "https://x.com"


def test_budget_max_search_guard_no_api_call():
    # search_count가 MAX_SEARCH(8) 이상이면 API 호출 없이 [] + degraded
    hits, cnt, deg = asyncio.run(web_search_budgeted("new", {}, 8))
    assert hits == [] and cnt == 8 and deg is True
