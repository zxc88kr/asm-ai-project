"""
애플리케이션 전역 설정 관리 모듈.

.env 파일의 환경 변수(Upstage Solar API, Amadeus API 키, 서버 포트 등)를
Pydantic Settings로 읽어 들여 타입 검증된 단일 `settings` 객체로 노출합니다.
다른 모든 모듈은 환경 변수에 직접 접근하지 않고 반드시 이 `settings`를 import 하여 사용합니다.

    from app.core.config import settings
    api_key = settings.UPSTAGE_API_KEY
"""

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py 기준으로 프로젝트 루트(레포 최상단)를 계산합니다.
# config.py -> core -> app -> backend -> (repo root)
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_ENV_FILE = _PROJECT_ROOT / ".env"

# .env 를 실제 프로세스 환경 변수(os.environ)에도 적재한다.
# pydantic Settings 는 .env 를 자체적으로만 읽으므로, os.getenv 로 키를 읽는
# 일부 모듈(intent_classifier, airscraper_client 등)도 동일한 키를 보도록 보장한다.
# override=False 라서 이미 설정된 실제 환경 변수는 덮어쓰지 않는다.
load_dotenv(_ENV_FILE, override=False)


class Settings(BaseSettings):
    """프로젝트 환경 변수 규격.

    .env 에 값이 없어도 서버가 죽지 않도록 모든 키 항목은 기본값(빈 문자열)을 가집니다.
    실제 API 키 유무는 `has_upstage_key` / `has_amadeus_key` 프로퍼티로 판별하며,
    키가 없을 경우 각 서비스 모듈이 더미(fallback) 응답으로 동작합니다.
    """

    # --- 1. LLM API (Upstage Solar) ---
    UPSTAGE_API_KEY: str = ""
    # Upstage는 OpenAI 호환 엔드포인트를 제공합니다.
    UPSTAGE_BASE_URL: str = "https://api.upstage.ai/v1"
    SOLAR_MODEL: str = "solar-pro2"

    # --- 2. 항공권 검색 API ---
    # 현재는 RapidAPI Sky-Scrapper(AirScraper)를 사용한다. (Amadeus 대체)
    RAPIDAPI_KEY: str = ""
    RAPIDAPI_FLIGHT_HOST: str = "sky-scrapper.p.rapidapi.com"
    # (구) Amadeus 설정 — 미사용. 호환을 위해 필드만 유지.
    AMADEUS_API_KEY: str = ""
    AMADEUS_API_SECRET: str = ""

    # --- 3. Server Config ---
    PORT: int = 8000

    # --- 4. Paths (런타임 계산값) ---
    # 세션별 메모리 JSON이 저장되는 디렉토리. memory/store.py 가 참조합니다.
    MEMORY_DATA_DIR: Path = _PROJECT_ROOT / "backend" / "app" / "memory" / "data"
    # 프론트엔드 빌드 결과물이 모이는 정적 파일 디렉토리. main.py 가 마운트합니다.
    STATIC_DIR: Path = _PROJECT_ROOT / "backend" / "static"

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        # .env 에 정의되지 않은 추가 환경 변수가 있어도 무시하고 통과합니다.
        extra="ignore",
    )

    @property
    def has_upstage_key(self) -> bool:
        """Upstage 키가 실제로 설정되었는지 여부.

        .env 템플릿의 placeholder('your_..._here')는 미설정으로 간주합니다.
        """
        return bool(self.UPSTAGE_API_KEY) and "your_" not in self.UPSTAGE_API_KEY

    @property
    def has_amadeus_key(self) -> bool:
        """Amadeus 키가 실제로 설정되었는지 여부."""
        return (
            bool(self.AMADEUS_API_KEY)
            and bool(self.AMADEUS_API_SECRET)
            and "your_" not in self.AMADEUS_API_KEY
        )


@lru_cache
def get_settings() -> Settings:
    """싱글톤 Settings 인스턴스 반환.

    lru_cache 로 최초 1회만 .env 를 파싱하고 이후 동일 객체를 재사용합니다.
    """
    return Settings()


# 편의를 위한 모듈 레벨 싱글톤. 대부분의 모듈은 이 객체를 직접 import 합니다.
settings = get_settings()
