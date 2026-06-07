from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.catalog import SOURCES, TOPICS
from backend.app.config import WEB_DIR, get_settings
from backend.app.db import Repository
from backend.app.demo_scenarios import BRIEFING_PRESETS, DEMO_SCENARIOS
from backend.app.models import (
    BriefingHistoryItem,
    BriefingPreset,
    BriefingProfile,
    BriefingProfileInput,
    BriefingRequest,
    BriefingResponse,
    DemoScenario,
    Option,
    SourceStatus,
)
from backend.app.news_client import NewsClient
from backend.app.service import BriefingService, ValidationError
from backend.app.summarizer import Summarizer


settings = get_settings()
repository = Repository(settings.database_path)
news_client = NewsClient(settings.news_api_key)
summarizer = Summarizer(
    api_key=settings.upstage_api_key,
    model=settings.upstage_model,
    base_url=settings.upstage_base_url,
)
briefing_service = BriefingService(
    news_client=news_client,
    summarizer=summarizer,
    repository=repository,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    repository.init()
    yield


app = FastAPI(title="뉴스 요약 큐레이터 에이전트", version="0.2.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "environment": settings.app_env,
        "rss_enabled": True,
        "news_api_configured": bool(settings.news_api_key),
        "upstage_configured": bool(settings.upstage_api_key),
        "upstage_model": settings.upstage_model,
    }


@app.get("/api/sources", response_model=list[Option])
def get_sources() -> list[Option]:
    return [Option(id=source.id, label=source.label) for source in SOURCES]


@app.get("/api/sources/status", response_model=list[SourceStatus])
def get_source_statuses() -> list[SourceStatus]:
    return news_client.source_statuses()


@app.get("/api/topics", response_model=list[Option])
def get_topics() -> list[Option]:
    return [Option(id=topic.id, label=topic.label) for topic in TOPICS]


@app.get("/api/demo-scenarios", response_model=list[DemoScenario])
def get_demo_scenarios() -> list[DemoScenario]:
    return list(DEMO_SCENARIOS)


@app.get("/api/presets", response_model=list[BriefingPreset])
def get_presets() -> list[BriefingPreset]:
    return list(BRIEFING_PRESETS)


@app.get("/api/profiles", response_model=list[BriefingProfile])
def get_profiles() -> list[BriefingProfile]:
    return repository.list_profiles()


@app.post("/api/profiles", response_model=BriefingProfile)
def create_profile(profile: BriefingProfileInput) -> BriefingProfile:
    return repository.save_profile(profile)


@app.delete("/api/profiles/{profile_id}")
def delete_profile(profile_id: int) -> dict[str, bool]:
    deleted = repository.delete_profile(profile_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="저장 프로필을 찾을 수 없습니다.")
    return {"deleted": True}


@app.post("/api/briefings", response_model=BriefingResponse)
def create_briefing(request: BriefingRequest) -> BriefingResponse:
    try:
        briefing = briefing_service.create_briefing(request)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return BriefingResponse(status="ok", briefing=briefing)


@app.get("/api/briefings/history", response_model=list[BriefingHistoryItem])
def briefing_history() -> list[BriefingHistoryItem]:
    return briefing_service.list_history()


@app.get("/api/briefings/{briefing_id}", response_model=BriefingResponse)
def get_briefing(briefing_id: int) -> BriefingResponse:
    briefing = briefing_service.get_briefing(briefing_id)
    if not briefing:
        raise HTTPException(status_code=404, detail="브리핑 기록을 찾을 수 없습니다.")
    return BriefingResponse(status="ok", briefing=briefing)
