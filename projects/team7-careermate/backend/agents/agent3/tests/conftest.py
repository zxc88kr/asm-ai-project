"""pytest 공용 픽스처 & 결정론 보장.

모든 테스트를 오프라인·결정론으로 돌리기 위해 LLM/검색 API 키를 제거한다.
  - UPSTAGE_API_KEY 없음 → llm은 규칙기반 폴백 경로 사용(네트워크 없음)
  - TAVILY_API_KEY 없음 → web_search는 DuckDuckGo 경로(테스트에선 호출 자체를 피함)

agent3/.env에 키가 있어도 import 시 로드된 값을 monkeypatch로 제거하므로 안전하다.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def force_offline(monkeypatch):
    """모든 테스트에서 LLM/검색 키 제거 → 폴백 경로 강제."""
    monkeypatch.delenv("UPSTAGE_API_KEY", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)


def load_fixture(name: str) -> dict:
    with open(FIXTURES / name, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def profile_frontend():
    from agents.agent3.models import ProfileDiagnosis

    return ProfileDiagnosis(**load_fixture("profile_frontend.json"))


@pytest.fixture
def profile_backend():
    from agents.agent3.models import ProfileDiagnosis

    return ProfileDiagnosis(**load_fixture("profile_backend.json"))


@pytest.fixture
def job_frontend():
    from agents.agent3.models import JobRequirement

    return JobRequirement(
        required_skills=["React로 화면을 컴포넌트 기반으로 구현하는 능력", "TypeScript로 타입 안전한 코드 작성"],
        preferred_skills=["상태관리 라이브러리 사용 경험"],
        keywords=["React", "TypeScript", "상태관리"],
        evidence_strength="strong",
    )
