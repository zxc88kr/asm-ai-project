"""skill_db.json 무결성 — prereq/role/alias 참조 유효성 + DAG(사이클 없음)."""

from __future__ import annotations

import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "skill_db.json"


def _load():
    with open(DB_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_prereqs_reference_existing_skills():
    db = _load()
    keys = set(db["skills"])
    for name, rec in db["skills"].items():
        for p in rec["prereqs"]:
            assert p in keys, f"{name}의 선행 {p!r}가 skills에 없음"


def test_roles_reference_existing_skills():
    db = _load()
    keys = set(db["skills"])
    for role, skills in db["roles"].items():
        for s in skills:
            assert s in keys, f"{role}의 {s!r}가 skills에 없음"


def test_aliases_reference_existing_skills():
    db = _load()
    keys = set(db["skills"])
    for alias, target in db["aliases"].items():
        assert target in keys, f"alias {alias!r} 타깃 {target!r}가 skills에 없음"


def test_role_aliases_reference_existing_roles():
    db = _load()
    role_keys = set(db["roles"])
    for alias, target in db.get("role_aliases", {}).items():
        assert target in role_keys, f"role_alias {alias!r} 타깃 {target!r}가 roles에 없음"
        assert alias == alias.lower(), f"role_alias 키 {alias!r}는 소문자여야(매칭 일관성)"


def test_no_prereq_cycles():
    db = _load()
    skills = db["skills"]
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {k: WHITE for k in skills}

    def dfs(u):
        color[u] = GRAY
        for v in skills[u]["prereqs"]:
            if color[v] == GRAY:
                return True
            if color[v] == WHITE and dfs(v):
                return True
        color[u] = BLACK
        return False

    for k in skills:
        if color[k] == WHITE:
            assert not dfs(k), f"prereq 사이클 발견: {k}"


def test_resource_fields_complete():
    db = _load()
    for name, rec in db["skills"].items():
        assert isinstance(rec["typical_hours"], int)
        for r in rec["resources"]:
            for field in ("title", "url", "type", "verified"):
                assert field in r, f"{name} 자원에 {field} 누락"


def test_two_roles_present():
    db = _load()
    assert "백엔드 개발자" in db["roles"]
    assert "프론트엔드 개발자" in db["roles"]
