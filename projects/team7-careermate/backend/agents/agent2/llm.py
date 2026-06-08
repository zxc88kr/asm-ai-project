from __future__ import annotations

import json
import os
import re

from openai import OpenAI

from .models import CompanyEvidence, JobPostingHit, JobRequirement


UPSTAGE_BASE_URL = os.getenv("UPSTAGE_BASE_URL", "https://api.upstage.ai/v1")
DEFAULT_SOLAR_MODEL = os.getenv("UPSTAGE_SOLAR_MODEL", "solar-pro3")


async def extract_with_solar(
    target_role: str,
    company_type: str | None,
    search_query: str,
    postings: list[JobPostingHit],
    max_companies: int = 5,
) -> JobRequirement:
    max_companies = max(1, min(10, max_companies))
    if not postings:
        return _fallback_extract(
            target_role,
            company_type,
            search_query,
            postings,
            "No recent role-relevant postings found",
            max_companies,
        )

    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        return _fallback_extract(
            target_role,
            company_type,
            search_query,
            postings,
            "UPSTAGE_API_KEY is not set",
            max_companies,
        )

    context = _build_context(postings)
    prompt = f"""
당신은 CareerMate의 Agent2(JobRequirementAgent)입니다.
입력은 목표직무와 희망기업유형뿐이며, 검색으로 수집한 채용공고 정보를 근거로 직무 요구역량을 추출해야 합니다.

목표직무: {target_role}
희망기업유형: {company_type or "미지정"}
검색쿼리: {search_query}

검색/수집 결과:
{context}

규칙:
- companies에는 근거로 사용한 실제 채용 기업명을 채용공고 제목/본문에서 추출하고 URL을 함께 넣으세요.
- LinkedIn, Wanted, 원티드, Jumpit, Glassdoor, Naver, Bing처럼 공고를 보여주는 플랫폼명은 기업명으로 쓰지 마세요.
- required_skills와 preferred_skills는 기술명만 쓰지 말고, "Python으로 API 서버를 구현하고 디버깅하는 능력"처럼 20~45자 내외의 짧은 자연어로 쓰세요.
- 채용공고 근거가 있는 기술/역량만 required_skills 또는 preferred_skills에 넣으세요.
- 최근 1년 이내 공고로 보이는 검색 결과만 근거로 삼으세요. 오래된/마감/종료 공고로 보이면 제외하세요.
- 홍보 문구, 복지, 태도 표현은 제외하세요.
- source_urls에는 근거로 사용한 URL만 넣으세요.
- evidence_strength는 공고 텍스트와 snippet이 충분하면 strong, 근거가 약하면 weak입니다.
- 반드시 아래 JSON 스키마만 반환하세요. 마크다운 코드블록은 쓰지 마세요.

{{
  "companies": [{{"name": "string", "url": "https://..."}}],
  "required_skills": ["string"],
  "preferred_skills": ["string"],
  "required_experience": ["string"],
  "keywords": ["string"],
  "evidence_strength": "strong|weak",
  "source_urls": ["https://..."],
  "summary": "한국어 2-4문장 요약"
}}
""".strip()

    try:
        client = OpenAI(api_key=api_key, base_url=UPSTAGE_BASE_URL)
        response = client.chat.completions.create(
            model=DEFAULT_SOLAR_MODEL,
            messages=[
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or "{}"
        data = _parse_json_object(content)
        return JobRequirement(
            companies=_complete_companies(
                _company_evidence(data.get("companies"), postings, max_companies),
                postings,
                max_companies,
            ),
            required_skills=_as_list(data.get("required_skills")),
            preferred_skills=_as_list(data.get("preferred_skills")),
            required_experience=_as_list(data.get("required_experience")),
            keywords=_as_list(data.get("keywords")),
            evidence_strength=data.get("evidence_strength", "weak")
            if data.get("evidence_strength") in {"strong", "weak"}
            else "weak",
            source="duckduckgo",
            source_urls=_valid_source_urls(_as_list(data.get("source_urls")), postings),
            postings=postings,
            summary=str(data.get("summary") or ""),
            search_query=search_query,
            llm_used=True,
        )
    except Exception as exc:
        return _fallback_extract(target_role, company_type, search_query, postings, exc.__class__.__name__, max_companies)


def _build_context(postings: list[JobPostingHit]) -> str:
    blocks = []
    for index, posting in enumerate(postings, start=1):
        body = posting.fetched_text or posting.snippet
        blocks.append(
            f"[{index}] {posting.title}\nURL: {posting.url}\nSNIPPET: {posting.snippet}\nTEXT:\n{body[:2500]}"
        )
    return "\n\n".join(blocks) if blocks else "검색 결과 없음"


def _parse_json_object(content: str) -> dict:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?", "", content).strip()
        content = re.sub(r"```$", "", content).strip()
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        content = match.group(0)
    return json.loads(content)


def _as_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _valid_source_urls(urls: list[str], postings: list[JobPostingHit]) -> list[str]:
    known = {posting.url for posting in postings}
    valid = [url for url in urls if url in known]
    return valid or [posting.url for posting in postings[:3]]


def _company_evidence(value: object, postings: list[JobPostingHit], max_companies: int) -> list[CompanyEvidence]:
    companies: list[CompanyEvidence] = []
    seen: set[str] = set()
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                name = str(item.get("name") or "").strip()
                url = str(item.get("url") or "").strip() or None
                posting_url = _find_company_posting_url(name, url, postings)
                if name and posting_url and _is_valid_company_name(name) and name not in seen:
                    companies.append(CompanyEvidence(name=name, url=posting_url))
                    seen.add(name)
            elif isinstance(item, str) and item.strip():
                name = item.strip()
                posting_url = _find_company_posting_url(name, None, postings)
                if posting_url and _is_valid_company_name(name) and name not in seen:
                    companies.append(CompanyEvidence(name=name, url=posting_url))
                    seen.add(name)
            if len(companies) >= max_companies:
                break
    if companies:
        return companies[:max_companies]
    return _companies_from_postings(postings, max_companies)


def _fallback_extract(
    target_role: str,
    company_type: str | None,
    search_query: str,
    postings: list[JobPostingHit],
    reason: str,
    max_companies: int = 5,
) -> JobRequirement:
    text = " ".join(
        [target_role, company_type or ""]
        + [posting.title for posting in postings]
        + [posting.snippet for posting in postings]
        + [posting.fetched_text[:1500] for posting in postings if posting.fetched_text]
    )
    skill_candidates = [
        "Python",
        "Java",
        "JavaScript",
        "TypeScript",
        "React",
        "Vue",
        "Next.js",
        "Node.js",
        "Spring",
        "Spring Boot",
        "FastAPI",
        "Django",
        "SQL",
        "PostgreSQL",
        "MySQL",
        "MongoDB",
        "Redis",
        "Docker",
        "Kubernetes",
        "AWS",
        "Git",
        "REST API",
        "GraphQL",
        "CI/CD",
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "Machine Learning",
        "Statistics",
        "Data Visualization",
        "Experiment Design",
    ]
    found = [skill for skill in skill_candidates if skill.lower() in text.lower()]
    if not found:
        found = _role_defaults(target_role)

    return JobRequirement(
        companies=_complete_companies(_companies_from_postings(postings, max_companies), postings, max_companies),
        required_skills=[_skill_sentence(skill, target_role) for skill in found[:7]],
        preferred_skills=[_skill_sentence(skill, target_role) for skill in found[7:10]],
        required_experience=_fallback_experience(target_role, bool(postings)),
        keywords=list(dict.fromkeys([target_role, company_type or "", *found]))[:10],
        evidence_strength="weak",
        source="duckduckgo" if postings else "role_inference",
        source_urls=[posting.url for posting in postings[:3]],
        postings=postings,
        summary="Solar LLM 추출에 실패해 검색 결과와 직무명 기반 규칙 폴백으로 요약했습니다.",
        search_query=search_query,
        llm_used=False,
        degraded_reason=reason,
    )


def _role_defaults(target_role: str) -> list[str]:
    role = target_role.lower()
    if "프론트" in target_role or "frontend" in role:
        return ["HTML/CSS", "JavaScript", "TypeScript", "React", "Git"]
    if "사이언티스트" in target_role or "scientist" in role:
        return ["Python", "SQL", "Pandas", "Scikit-learn", "Statistics", "Data Visualization", "Experiment Design"]
    if "데이터" in target_role or "data" in role:
        return ["Python", "SQL", "Pandas", "Data Visualization", "Statistics", "Git"]
    if "백엔드" in target_role or "backend" in role:
        return ["Python", "Java", "Spring Boot", "FastAPI", "SQL", "Docker", "Git"]
    return ["Git", "REST API", "SQL"]


def _companies_from_postings(postings: list[JobPostingHit], max_companies: int = 5) -> list[CompanyEvidence]:
    companies: list[CompanyEvidence] = []
    seen: set[str] = set()
    for posting in postings:
        candidates = [
            _extract_company_name(posting.title),
            _extract_company_name(posting.snippet),
            _extract_company_name(posting.fetched_text.splitlines()[0] if posting.fetched_text else ""),
        ]
        for name in candidates:
            if name and _is_valid_company_name(name) and name not in seen:
                companies.append(CompanyEvidence(name=name, url=posting.url))
                seen.add(name)
                break
        if len(companies) >= max_companies:
            break
    return companies[:max_companies]


def _complete_companies(
    companies: list[CompanyEvidence],
    postings: list[JobPostingHit],
    max_companies: int,
) -> list[CompanyEvidence]:
    completed: list[CompanyEvidence] = []
    seen: set[str] = set()

    for company in companies + _companies_from_postings(postings, max_companies):
        posting_url = _find_company_posting_url(company.name, company.url, postings)
        if company.name and posting_url and _is_valid_company_name(company.name) and company.name not in seen:
            completed.append(CompanyEvidence(name=company.name, url=posting_url))
            seen.add(company.name)
        if len(completed) >= max_companies:
            return completed

    return completed


def _find_company_posting_url(name: str, url: str | None, postings: list[JobPostingHit]) -> str | None:
    if not name:
        return None

    normalized_name = name.lower()
    for posting in postings:
        posting_text = " ".join([posting.title, posting.snippet, posting.fetched_text]).lower()
        if normalized_name in posting_text:
            return posting.url

    return None


def _fallback_company_names(company_type: str | None) -> list[str]:
    text = (company_type or "").lower()
    if "대기업" in (company_type or "") or "enterprise" in text:
        return ["삼성전자", "현대자동차", "LG전자", "SK텔레콤", "네이버", "카카오", "쿠팡", "토스", "라인", "우아한형제들"]
    if "스타트" in (company_type or "") or "startup" in text:
        return ["토스", "당근", "오늘의집", "무신사", "직방", "야놀자", "컬리", "뤼튼", "리멤버", "센드버드"]
    if "중견" in (company_type or ""):
        return ["NHN", "더존비즈온", "한글과컴퓨터", "컴투스", "위메이드", "네오위즈", "안랩", "메가존클라우드", "다우기술", "티맥스소프트"]
    return ["네이버", "카카오", "쿠팡", "토스", "라인", "당근", "우아한형제들", "오늘의집", "무신사", "야놀자"]


def _extract_company_name(title: str) -> str:
    title = _remove_platform_noise(title)
    patterns = [
        r"^\[([^\]]+)\]",
        r"^(.+?)\s+백엔드\s+팀",
        r"^(.+?)\s+Backend",
        r"^(.+?)\s+백엔드",
        r"^(.+?)\s+프론트엔드",
        r"^(.+?)\s+데이터",
        r"^(.+?)\s*[-|]\s*채용",
        r"^(.+?)\s+채용",
    ]
    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            name = match.group(1).strip()
            if 1 <= len(name) <= 40:
                return name
    return ""


def _remove_platform_noise(title: str) -> str:
    cleaned = re.sub(r"\s*\|\s*(원티드|wanted|jumpit|점핏|linkedin|glassdoor).*$", "", title, flags=re.I)
    cleaned = re.sub(r"\s*-\s*(LinkedIn|Glassdoor).*$", "", cleaned, flags=re.I)
    cleaned = re.sub(r"^LinkedIn\s+\S+\s+[?›>]\s+", "", cleaned, flags=re.I)
    cleaned = cleaned.replace("채용 공고", "채용")
    return cleaned.strip()


def _is_valid_company_name(name: str) -> bool:
    platform_names = {
        "linkedin",
        "linkedIn",
        "원티드",
        "wanted",
        "jumpit",
        "점핏",
        "glassdoor",
        "startup jobs",
        "naver",
        "bing",
        "duckduckgo",
        "채용",
        "채용공고",
        "백엔드",
        "프론트엔드",
        "데이터",
    }
    invalid_fragments = (
        "백엔드",
        "프론트",
        "데이터",
        "data engineer",
        "개발",
        "엔지니어",
        "developer",
        "backend",
        "frontend",
        "blockchain",
        "블록체인",
        "서버",
        "채용",
        "시니어",
        "주니어",
        "팀장",
        "리드",
    )
    normalized = re.sub(r"\s+", " ", name).strip().lower()
    return (
        1 <= len(name.strip()) <= 40
        and normalized not in {item.lower() for item in platform_names}
        and not any(fragment in normalized for fragment in invalid_fragments)
        and "(" not in name
        and ")" not in name
    )


def _fallback_experience(target_role: str, has_postings: bool) -> list[str]:
    role = target_role.lower()
    if "사이언티스트" in target_role or "scientist" in role:
        return [
            "데이터 분석 또는 머신러닝 모델링 프로젝트를 수행한 경험",
            "비즈니스 문제를 지표와 실험으로 검증한 경험",
        ]
    if "데이터" in target_role or "data" in role:
        return ["데이터 분석 프로젝트를 수행하고 결과를 설명한 경험"]
    if has_postings:
        return ["채용공고 원문 기반 경험 요건 확인 필요"]
    return []


def _skill_sentence(skill: str, target_role: str = "") -> str:
    role = target_role.lower()
    if "사이언티스트" in target_role or "scientist" in role or "데이터" in target_role or "data" in role:
        data_templates = {
            "Python": "Python으로 데이터를 분석하고 모델링 실험을 수행하는 능력",
            "SQL": "SQL로 필요한 데이터를 추출하고 분석용 테이블을 구성하는 능력",
            "Git": "Git으로 분석 코드와 실험 이력을 관리하는 능력",
        }
        if skill in data_templates:
            return data_templates[skill]

    templates = {
        "Python": "Python으로 서버 로직을 구현하고 디버깅하는 능력",
        "Java": "Java로 안정적인 백엔드 서비스를 구현하는 능력",
        "JavaScript": "JavaScript로 웹 서비스 동작을 구현하는 능력",
        "TypeScript": "TypeScript로 타입 안정적인 코드를 작성하는 능력",
        "React": "React로 사용자 화면을 컴포넌트 기반으로 구현하는 능력",
        "Spring Boot": "Spring Boot로 REST API 서버를 설계하고 구현하는 능력",
        "FastAPI": "FastAPI로 Python 기반 API 서버를 구현하는 능력",
        "SQL": "SQL로 데이터를 조회하고 모델링하는 능력",
        "MySQL": "MySQL로 서비스 데이터를 설계하고 운영하는 능력",
        "PostgreSQL": "PostgreSQL로 관계형 데이터를 설계하고 최적화하는 능력",
        "Docker": "Docker로 애플리케이션 실행 환경을 구성하는 능력",
        "AWS": "AWS 클라우드에서 서비스를 배포하고 운영하는 능력",
        "Git": "Git으로 협업 흐름과 코드 이력을 관리하는 능력",
        "REST API": "REST API를 설계하고 클라이언트와 연동하는 능력",
        "CI/CD": "CI/CD로 배포 과정을 자동화하고 안정화하는 능력",
        "Pandas": "Pandas로 데이터를 정제하고 분석 가능한 형태로 가공하는 능력",
        "NumPy": "NumPy로 수치 데이터를 효율적으로 처리하는 능력",
        "Scikit-learn": "Scikit-learn으로 예측 모델을 학습하고 검증하는 능력",
        "Machine Learning": "머신러닝 모델을 설계하고 성능을 평가하는 능력",
        "Statistics": "통계적 가설을 세우고 데이터로 검증하는 능력",
        "Data Visualization": "분석 결과를 시각화해 인사이트로 전달하는 능력",
        "Experiment Design": "실험을 설계하고 지표 변화의 원인을 해석하는 능력",
    }
    return templates.get(skill, f"{skill}을 실무 과제에 적용하는 능력")
