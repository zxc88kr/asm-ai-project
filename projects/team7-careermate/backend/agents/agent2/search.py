from __future__ import annotations

from datetime import date, timedelta
import re
from urllib.parse import parse_qs, unquote, urlparse

import httpx
from bs4 import BeautifulSoup

from .models import JobPostingHit


DUCKDUCKGO_HTML_URL = "https://html.duckduckgo.com/html/"
BING_SEARCH_URL = "https://www.bing.com/search"
NAVER_SEARCH_URL = "https://search.naver.com/search.naver"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
)
TIMEOUT = httpx.Timeout(12.0, connect=8.0)
RECENT_DAYS = 365
EXPIRED_KEYWORDS = (
    "채용 종료",
    "접수 종료",
    "지원 종료",
    "모집 종료",
    "공고 종료",
    "closed",
    "expired",
    "no longer accepting",
)


def build_job_query(target_role: str, company_type: str | None) -> str:
    company = f" {company_type}" if company_type else ""
    return f"{target_role}{company} 채용공고"


async def search_job_postings(query: str, max_results: int = 5) -> list[JobPostingHit]:
    naver_html = await _fetch_naver_html(query)
    hits = _parse_naver_hits(naver_html, max_results) if naver_html else []
    if hits:
        return hits

    recent_html = await _fetch_duckduckgo_html(query, recent=True)
    hits = _parse_duckduckgo_hits(recent_html, max_results) if recent_html else []
    if hits:
        return hits

    fallback_html = await _fetch_duckduckgo_html(query, recent=False)
    hits = _parse_duckduckgo_hits(fallback_html, max_results) if fallback_html else []
    if hits:
        return hits

    bing_html = await _fetch_bing_html(query)
    hits = _parse_bing_hits(bing_html, max_results) if bing_html else []
    if hits:
        return hits

    return []


async def _fetch_duckduckgo_html(query: str, recent: bool) -> str:
    data = {"q": query}
    if recent:
        data["df"] = "y"
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            response = await client.post(
                DUCKDUCKGO_HTML_URL,
                data=data,
                headers={"User-Agent": USER_AGENT},
            )
            response.raise_for_status()
            return response.text
    except Exception:
        return ""


def _parse_duckduckgo_hits(html: str, max_results: int) -> list[JobPostingHit]:
    soup = BeautifulSoup(html, "html.parser")
    hits: list[JobPostingHit] = []
    seen: set[str] = set()

    links = soup.select("a.result__a") or soup.select("a[href]")
    for link in links:
        url = _clean_duckduckgo_url(link.get("href", ""))
        if not _looks_like_job_url(url) or url in seen:
            continue

        title = " ".join(link.get_text(" ", strip=True).split())
        if not title:
            continue

        result = link.find_parent(class_="result")
        snippet_tag = result.select_one(".result__snippet") if result else None
        snippet = ""
        if snippet_tag is not None:
            snippet = " ".join(snippet_tag.get_text(" ", strip=True).split())

        hits.append(JobPostingHit(title=title, url=url, snippet=snippet))
        seen.add(url)
        if len(hits) >= max_results:
            break

    return hits


async def _fetch_bing_html(query: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            response = await client.get(
                BING_SEARCH_URL,
                params={"q": query, "filters": 'ex1:"ez5_20032_20397"'},
                headers={"User-Agent": USER_AGENT},
            )
            response.raise_for_status()
            return response.text
    except Exception:
        return ""


def _parse_bing_hits(html: str, max_results: int) -> list[JobPostingHit]:
    soup = BeautifulSoup(html, "html.parser")
    hits: list[JobPostingHit] = []
    seen: set[str] = set()

    for result in soup.select("li.b_algo"):
        link = result.select_one("h2 a")
        if link is None:
            continue
        url = link.get("href", "")
        if not url or url in seen:
            continue

        title = " ".join(link.get_text(" ", strip=True).split())
        snippet_tag = result.select_one(".b_caption p")
        snippet = ""
        if snippet_tag is not None:
            snippet = " ".join(snippet_tag.get_text(" ", strip=True).split())

        hits.append(JobPostingHit(title=title, url=url, snippet=snippet, source="bing"))
        seen.add(url)
        if len(hits) >= max_results:
            break

    return hits


async def _fetch_naver_html(query: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            response = await client.get(
                NAVER_SEARCH_URL,
                params={"query": query},
                headers={"User-Agent": USER_AGENT},
            )
            response.raise_for_status()
            return response.text
    except Exception:
        return ""


def _parse_naver_hits(html: str, max_results: int) -> list[JobPostingHit]:
    soup = BeautifulSoup(html, "html.parser")
    hits: list[JobPostingHit] = []
    seen: set[str] = set()

    for link in soup.select("a"):
        url = link.get("href", "")
        if not _looks_like_job_url(url) or url in seen:
            continue
        title = " ".join(link.get_text(" ", strip=True).split())
        if not title:
            continue
        hits.append(JobPostingHit(title=title, url=url, snippet=title, source="naver"))
        seen.add(url)
        if len(hits) >= max_results:
            break

    return hits


def _looks_like_job_url(url: str) -> bool:
    if not url.startswith("http"):
        return False
    allowed_path_markers = (
        "wanted.co.kr/wd/",
        "jumpit.co.kr/position/",
        "career.programmers.co.kr/job_positions/",
        "jobs.lever.co/",
        "greenhouse.io/",
        "startup.jobs/",
        "glassdoor.",
    )
    blocked_markers = (
        "blog.naver.com",
        "tistory.com",
        "velog.io",
        "brunch.co.kr",
        "medium.com",
        "reddit.com",
    )
    parsed = urlparse(url)
    lowered = f"{parsed.netloc}{parsed.path}".lower()
    linkedin_job = "linkedin.com/jobs/view" in lowered
    return (linkedin_job or any(marker in lowered for marker in allowed_path_markers)) and not any(
        marker in lowered for marker in blocked_markers
    )


async def enrich_posting_texts(hits: list[JobPostingHit], max_pages: int = 3) -> list[JobPostingHit]:
    if not hits:
        return hits

    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        for index, hit in enumerate(hits):
            if index >= max_pages:
                break
            try:
                response = await client.get(hit.url, headers={"User-Agent": USER_AGENT})
                response.raise_for_status()
                text = _html_to_text(response.text)
                hit.fetched_text = text[:4000]
                hit.fetch_ok = len(hit.fetched_text) >= 120
            except Exception as exc:
                hit.fetch_ok = False
                hit.fetch_error = exc.__class__.__name__

    return hits


def filter_recent_postings(hits: list[JobPostingHit]) -> list[JobPostingHit]:
    return [
        hit
        for hit in hits
        if is_recent_job_text(hit.title, hit.snippet, hit.fetched_text)
    ]


def is_recent_job_text(*parts: str) -> bool:
    text = " ".join(part for part in parts if part).lower()
    if any(keyword in text for keyword in EXPIRED_KEYWORDS):
        return False

    explicit_dates = _extract_full_dates(text)
    if explicit_dates:
        return max(explicit_dates) >= date.today() - timedelta(days=RECENT_DAYS)

    return True


def _extract_full_dates(text: str) -> list[date]:
    found: list[date] = []
    patterns = [
        r"\b(20\d{2})[./-](\d{1,2})[./-](\d{1,2})\b",
        r"\b(20\d{2})년\s*(\d{1,2})월\s*(\d{1,2})일",
    ]
    for pattern in patterns:
        for year, month, day in re.findall(pattern, text):
            try:
                found.append(date(int(year), int(month), int(day)))
            except ValueError:
                continue
    return found


def _clean_duckduckgo_url(raw: str) -> str:
    if not raw:
        return ""
    if raw.startswith("//duckduckgo.com/l/?"):
        raw = "https:" + raw
    parsed = urlparse(raw)
    if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
        uddg = parse_qs(parsed.query).get("uddg", [""])[0]
        return unquote(uddg)
    return raw


def _html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
        tag.decompose()
    text = soup.get_text("\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text
