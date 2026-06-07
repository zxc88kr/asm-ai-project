from __future__ import annotations

from backend.app.models import BriefingPreset


BRIEFING_PRESETS: tuple[BriefingPreset, ...] = (
    BriefingPreset(
        id="commute-it-economy",
        label="오늘 IT·경제",
        description="업무 시작 전 확인하기 좋은 IT와 경제 주요 흐름",
        sources=["yonhap", "chosun", "hani", "khan", "mk"],
        topics=["it", "economy"],
        date_range="1d",
        limit=5,
    ),
    BriefingPreset(
        id="job-ai-week",
        label="AI·반도체 주간",
        description="최근 일주일의 AI, 반도체, 데이터센터 이슈",
        sources=["yonhap", "chosun", "hani", "khan", "mk"],
        topics=["ai"],
        custom_keywords=["반도체", "데이터센터"],
        date_range="7d",
        limit=5,
    ),
    BriefingPreset(
        id="market-company-week",
        label="기업·시장 브리핑",
        description="시장, 실적, 기업과 스타트업 흐름을 함께 보는 브리핑",
        sources=["yonhap", "chosun", "hani", "khan", "mk"],
        topics=["economy", "stock", "startup"],
        custom_keywords=["실적", "코스피"],
        date_range="7d",
        limit=5,
    ),
)

DEMO_SCENARIOS = BRIEFING_PRESETS
