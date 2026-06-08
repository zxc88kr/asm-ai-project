from __future__ import annotations

from .llm import extract_with_solar
from .models import Agent2Request, JobRequirement
from .search import (
    build_job_query,
    enrich_posting_texts,
    filter_recent_postings,
    search_job_postings,
)


async def run_agent2(request: Agent2Request) -> JobRequirement:
    query = build_job_query(request.target_role, request.company_type)
    postings = await _search_with_fallbacks(request, query)
    postings = await enrich_posting_texts(postings, max_pages=request.max_results)
    postings = filter_recent_postings(postings)
    postings = _filter_role_relevant(postings, request.target_role)
    return await extract_with_solar(
        target_role=request.target_role,
        company_type=request.company_type,
        search_query=query,
        postings=postings,
        max_companies=request.max_results,
    )


async def _search_with_fallbacks(request: Agent2Request, primary_query: str):
    english_role = _english_role_hint(request.target_role)
    english_company = _english_company_hint(request.company_type)
    company = request.company_type or ""
    queries = [
        primary_query,
        f"{request.target_role} {company} 채용공고",
        f"{request.target_role} {company} 채용",
        f"{request.target_role} {company} 개발자 채용",
        f"{request.target_role} 채용 원티드",
        f"{request.target_role} 채용 점핏",
        f"{request.target_role} 채용 프로그래머스",
        f"site:wanted.co.kr/wd {request.target_role} {company}",
        f"site:jumpit.co.kr/position {request.target_role} {company}",
        f"site:career.programmers.co.kr/job_positions {request.target_role} {company}",
        f"{english_role} {english_company} Korea jobs",
        f"{english_role} Korea Python FastAPI jobs",
    ]
    seen_urls: set[str] = set()
    postings = []
    for query in queries:
        hits = await search_job_postings(query, request.max_results)
        for hit in hits:
            if hit.url not in seen_urls:
                postings.append(hit)
                seen_urls.add(hit.url)
            if len(postings) >= request.max_results:
                return postings
    return postings


def _english_role_hint(target_role: str) -> str:
    lowered = target_role.lower()
    if "백엔드" in target_role or "backend" in lowered or "back-end" in lowered:
        return "backend developer"
    if "프론트" in target_role or "frontend" in lowered or "front-end" in lowered:
        return "frontend developer"
    if "사이언티스트" in target_role or "scientist" in lowered:
        return "data scientist"
    if "데이터" in target_role or "data" in lowered:
        return "data analyst data engineer"
    if "devops" in lowered or "데브옵스" in target_role:
        return "devops engineer"
    return target_role


def _english_company_hint(company_type: str | None) -> str:
    if not company_type:
        return ""
    lowered = company_type.lower()
    if "스타트" in company_type or "startup" in lowered:
        return "startup"
    if "대기업" in company_type:
        return "enterprise"
    if "중견" in company_type:
        return "mid-sized company"
    return company_type


def _filter_role_relevant(postings, target_role: str):
    terms = _role_relevance_terms(target_role)
    if not terms:
        return postings
    relevant = []
    for posting in postings:
        text = " ".join([posting.title, posting.snippet, posting.fetched_text]).lower()
        if any(term.lower() in text for term in terms):
            relevant.append(posting)
    return relevant


def _role_relevance_terms(target_role: str) -> list[str]:
    lowered = target_role.lower()
    if "백엔드" in target_role or "backend" in lowered or "back-end" in lowered:
        return ["백엔드", "backend", "back-end", "server", "서버", "api", "developer", "개발자"]
    if "프론트" in target_role or "frontend" in lowered or "front-end" in lowered:
        return ["프론트", "frontend", "front-end", "react", "javascript", "typescript", "개발자"]
    if "사이언티스트" in target_role or "scientist" in lowered:
        return ["데이터", "data", "scientist", "ml", "machine learning", "ai", "모델링", "통계", "python", "sql"]
    if "데이터" in target_role or "data" in lowered:
        return ["데이터", "data", "analyst", "engineer", "scientist", "sql", "python"]
    return [target_role]
