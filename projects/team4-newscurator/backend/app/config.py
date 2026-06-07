from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]
WEB_DIR = ROOT_DIR / "web"

load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    app_env: str
    news_api_key: str | None
    upstage_api_key: str | None
    upstage_model: str
    upstage_base_url: str
    database_path: Path


def get_settings() -> Settings:
    database_path = Path(os.getenv("DATABASE_PATH", "backend/data/briefings.db"))
    if not database_path.is_absolute():
        database_path = ROOT_DIR / database_path

    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        news_api_key=os.getenv("NEWS_API_KEY") or None,
        upstage_api_key=os.getenv("UPSTAGE_API_KEY") or None,
        upstage_model=os.getenv("UPSTAGE_MODEL", "solar-pro3"),
        upstage_base_url=os.getenv("UPSTAGE_BASE_URL", "https://api.upstage.ai/v1"),
        database_path=database_path,
    )
