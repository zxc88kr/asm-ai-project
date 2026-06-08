"""Agent3 툴 — ReAct 패턴의 Act(도구 호출) 구현.

두 종류의 외부 정보 획득 수단:
  - lookup_skill / list_skills_for_role / normalize_skill_name
      → 정적 JSON 스킬 사전(skill_db.json) 조회. LLM 없음, 결정론적.
  - web_search
      → 검색 API(DuckDuckGo HTML, 또는 TAVILY_API_KEY 있으면 Tavily) 호출.
        크롤링(대상 사이트 순회)이 아니라 검색 결과 메타데이터 수신.

공통 계약: **절대 예외를 던지지 않는다.** 실패 시 빈/unknown 폴백을 반환한다.
설계 근거: docs/04-tools-skill-db.md
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from .constants import DEFAULT_SEARCH_K
from .models import ResourceItem, SearchHit, SkillRecord, SkillStatus, SourceOrigin

_SKILL_DB_PATH = Path(__file__).parent / "skill_db.json"
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
)
_DUCKDUCKGO_HTML_URL = "https://html.duckduckgo.com/html/"
_TAVILY_URL = "https://api.tavily.com/search"


# ─────────────────────────────────────────────────────────────
# 스킬 DB 로딩 (1회 캐시)
# ─────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _load_db() -> dict:
    """skill_db.json을 1회 로드해 캐시. 실패 시 빈 구조 반환(throw 금지)."""
    try:
        with open(_SKILL_DB_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return {
            "skills": data.get("skills", {}),
            "roles": data.get("roles", {}),
            "aliases": data.get("aliases", {}),
            "role_aliases": data.get("role_aliases", {}),
        }
    except Exception:
        return {"skills": {}, "roles": {}, "aliases": {}, "role_aliases": {}}


# ─────────────────────────────────────────────────────────────
# normalize_skill_name — 자유표기 → 표준 키
# ─────────────────────────────────────────────────────────────
def normalize_skill_name(raw: str) -> str:
    """자유 표기를 스킬 사전 표준 키로 정규화.

    예: "react.js" → "React", "fast api" → "FastAPI", "파이썬" → "Python".
    매칭 실패 시 입력을 strip만 해서 그대로 반환(throw 금지).
    """
    if not raw or not raw.strip():
        return raw
    db = _load_db()
    skills = db["skills"]
    aliases = db["aliases"]

    stripped = raw.strip()
    # 1) 이미 표준 키
    if stripped in skills:
        return stripped
    # 2) alias 매칭 (소문자 기준)
    lowered = stripped.lower()
    if lowered in aliases:
        return aliases[lowered]
    # 3) 대소문자 무시 키 매칭
    for key in skills:
        if key.lower() == lowered:
            return key
    # 4) 실패 → 원문(strip)
    return stripped


# ─────────────────────────────────────────────────────────────
# lookup_skill — 정적 사전 조회
# ─────────────────────────────────────────────────────────────
def lookup_skill(name: str) -> SkillRecord:
    """IT 스킬 사전 조회. 미존재/오류 시 status=unknown 폴백(throw 금지).

    known이면 resources는 origin="db", verified=True로 채워진다.
    """
    try:
        normalized = normalize_skill_name(name)
        skills = _load_db()["skills"]
        rec = skills.get(normalized)
        if rec is None:
            return _unknown_record(normalized)

        resources = [
            ResourceItem(
                title=r.get("title", ""),
                url=r.get("url"),
                type=r.get("type", "doc"),
                verified=bool(r.get("verified", True)),
                origin=SourceOrigin.db,
            )
            for r in rec.get("resources", [])
        ]
        return SkillRecord(
            name=normalized,
            status=SkillStatus.known,
            prereqs=list(rec.get("prereqs", [])),
            resources=resources,
            typical_hours=int(rec.get("typical_hours", 0)),
            verified=True,
        )
    except Exception:
        return _unknown_record(name)


def _unknown_record(name: str) -> SkillRecord:
    return SkillRecord(
        name=name,
        status=SkillStatus.unknown,
        prereqs=[],
        resources=[],
        typical_hours=0,
        verified=False,
    )


# ─────────────────────────────────────────────────────────────
# normalize_role_name — 자유 직무표기 → 표준 직무 키
# ─────────────────────────────────────────────────────────────
def normalize_role_name(raw: str) -> str:
    """직무 자유표기를 스킬DB 표준 직무 키로 정규화.

    예: "프론트엔드 엔지니어" → "프론트엔드 개발자", "ML engineer" → "머신러닝 엔지니어".
    매칭 실패 시 입력을 strip만 해서 그대로 반환(throw 금지).
    """
    if not raw or not raw.strip():
        return raw
    db = _load_db()
    roles = db["roles"]
    role_aliases = db["role_aliases"]

    stripped = raw.strip()
    if stripped in roles:                 # 이미 표준 직무 키
        return stripped
    lowered = stripped.lower()
    if lowered in role_aliases:           # 직무 별칭 매칭
        return role_aliases[lowered]
    for key in roles:                     # 대소문자 무시 키 매칭
        if key.lower() == lowered:
            return key
    return stripped


# ─────────────────────────────────────────────────────────────
# list_skills_for_role — 직무별 스킬 일괄 조회
# ─────────────────────────────────────────────────────────────
def list_skills_for_role(role: str) -> list[SkillRecord]:
    """직무명으로 관련 SkillRecord 일괄 조회. 미매핑 시 빈 리스트(throw 금지).

    normalize_role_name으로 직무 별칭/표기 변형을 표준 키로 보정한 뒤 조회한다.
    """
    try:
        roles = _load_db()["roles"]
        skill_names = roles.get(normalize_role_name(role))
        if not skill_names:
            return []
        return [lookup_skill(s) for s in skill_names]
    except Exception:
        return []


# ─────────────────────────────────────────────────────────────
# web_search — 검색 API 어댑터 (DuckDuckGo / Tavily)
# ─────────────────────────────────────────────────────────────
async def web_search(query: str, k: int = DEFAULT_SEARCH_K) -> list[SearchHit]:
    """검색 API를 호출해 상위 k개 SearchHit을 반환한다.

    제공자 선택:
      - TAVILY_API_KEY 환경변수 있으면 Tavily (JSON API, 더 안정적)
      - 없으면 DuckDuckGo HTML (키 불필요, agent2와 동일 방식)

    계약: **절대 예외를 던지지 않는다.** 실패 시 빈 리스트 [] 반환.
    캐시·search_count·MAX_SEARCH 가드는 호출 노드가 관리한다(이 함수는 순수 어댑터).
    """
    if not query or not query.strip():
        return []
    try:
        if os.getenv("TAVILY_API_KEY"):
            return await _tavily_search(query, k)
        return await _duckduckgo_search(query, k)
    except Exception:
        return []


async def _tavily_search(query: str, k: int) -> list[SearchHit]:
    import httpx

    payload = {
        "api_key": os.getenv("TAVILY_API_KEY", ""),
        "query": query,
        "max_results": k,
        "search_depth": "basic",
    }
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(12.0, connect=8.0)) as client:
            resp = await client.post(_TAVILY_URL, json=payload)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return []

    now = _now_iso()
    hits: list[SearchHit] = []
    for item in (data.get("results") or [])[:k]:
        url = item.get("url", "")
        if not url:
            continue
        hits.append(
            SearchHit(
                title=item.get("title", ""),
                url=url,
                snippet=item.get("content", ""),
                source=urlparse(url).netloc or "tavily",
                retrieved_at=now,
            )
        )
    return hits


async def _duckduckgo_search(query: str, k: int) -> list[SearchHit]:
    import httpx
    from bs4 import BeautifulSoup

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(12.0, connect=8.0), follow_redirects=True
        ) as client:
            resp = await client.post(
                _DUCKDUCKGO_HTML_URL,
                data={"q": query},
                headers={"User-Agent": _USER_AGENT},
            )
            resp.raise_for_status()
            html = resp.text
    except Exception:
        return []

    soup = BeautifulSoup(html, "html.parser")
    now = _now_iso()
    hits: list[SearchHit] = []
    seen: set[str] = set()

    for result in soup.select(".result"):
        link = result.select_one("a.result__a")
        if link is None:
            continue
        url = _clean_ddg_url(link.get("href", ""))
        if not url or url in seen:
            continue
        title = " ".join(link.get_text(" ", strip=True).split())
        snippet_tag = result.select_one(".result__snippet")
        snippet = (
            " ".join(snippet_tag.get_text(" ", strip=True).split())
            if snippet_tag is not None
            else ""
        )
        hits.append(
            SearchHit(
                title=title,
                url=url,
                snippet=snippet,
                source=urlparse(url).netloc or "duckduckgo",
                retrieved_at=now,
            )
        )
        seen.add(url)
        if len(hits) >= k:
            break
    return hits


def _clean_ddg_url(raw: str) -> str:
    """DuckDuckGo 리디렉트 래퍼(//duckduckgo.com/l/?uddg=...)에서 실제 url 추출."""
    if not raw:
        return ""
    if raw.startswith("//duckduckgo.com/l/?"):
        raw = "https:" + raw
    parsed = urlparse(raw)
    if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
        uddg = parse_qs(parsed.query).get("uddg", [""])[0]
        return unquote(uddg)
    return raw


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─────────────────────────────────────────────────────────────
# 검색 예산 헬퍼 — 노드가 캐시·카운트·MAX_SEARCH를 일관되게 다루도록 보조
# ─────────────────────────────────────────────────────────────
async def web_search_budgeted(
    query: str,
    search_results: dict[str, list[SearchHit]],
    search_count: int,
    k: int = DEFAULT_SEARCH_K,
) -> tuple[list[SearchHit], int, bool]:
    """캐시·MAX_SEARCH 가드를 적용한 web_search 래퍼.

    Returns: (hits, new_search_count, degraded)
      - 캐시 히트: 카운트 미증가, degraded=False
      - MAX_SEARCH 초과: API 미호출, [] 반환, degraded=True
      - API 실패: [] 반환, degraded=True (카운트는 증가)
    """
    from .constants import MAX_SEARCH

    if query in search_results:
        return search_results[query], search_count, False

    if search_count >= MAX_SEARCH:
        return [], search_count, True

    hits = await web_search(query, k)
    new_count = search_count + 1
    search_results[query] = hits
    degraded = len(hits) == 0
    return hits, new_count, degraded
