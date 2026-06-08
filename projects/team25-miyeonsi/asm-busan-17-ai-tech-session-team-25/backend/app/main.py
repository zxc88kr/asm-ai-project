"""
FastAPI 애플리케이션 진입점.

- /api/* : 게임 API 라우터(routes.py) 마운트
- /      : 프론트엔드 빌드 결과물(backend/static)을 정적 서빙(SPA)

프론트엔드를 빌드해 static 디렉토리로 복사하면 단일 서버에서 UI+API가 함께 동작한다.
빌드 결과물이 아직 없는 개발 초기에는 정적 마운트를 건너뛰고 API만 노출한다.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.core.config import settings

app = FastAPI(title="Travel Mate Agent API")

# ==========================================
# CORS 미들웨어 설정 (Local Development 용)
# ==========================================
# 프론트엔드(예: http://localhost:5173)와 백엔드(http://localhost:8000)의
# 포트가 서로 다르기 때문에, 브라우저의 자원 공유 차단(CORS)을 해제해 주어야 합니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 로컬 개발 단계이므로 모든 도메인에서의 접근을 허용합니다.
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, OPTIONS 등 모든 HTTP 메서드 허용
    allow_headers=["*"],  # Content-Type 등 모든 헤더 허용
)

# API 라우터 등록
# 모든 게임 및 대화 관련 API는 자동으로 "/api" 접두사가 붙습니다. (예: /api/chat)
app.include_router(api_router, prefix="/api")


@app.get("/api/health")
async def health() -> dict:
    """헬스 체크 엔드포인트."""
    return {
        "status": "healthy",
        "llm_available": settings.has_upstage_key,
        "message": "Travel Mate Agent API가 정상 작동 중입니다.",
    }


# ==========================================
# 정적 파일(프론트엔드 빌드 결과) 서빙
# ==========================================
# backend/static 에 프론트엔드 빌드 산출물(index.html, assets/...)이 있으면 마운트합니다.
# StaticFiles(html=True)는 디렉토리 진입 시 index.html을 자동 반환합니다.
_STATIC_DIR = Path(settings.STATIC_DIR)
_INDEX_FILE = _STATIC_DIR / "index.html"

if _INDEX_FILE.exists():
    # 빌드 산출물이 있을 때: 전체 SPA 서빙
    # /assets 등 실제 정적 자원을 먼저 서빙하고, 매칭 안 되는 경로는 SPA 라우팅을 위해
    # index.html로 폴백한다(클라이언트 사이드 라우터 대응).
    app.mount("/assets", StaticFiles(directory=str(_STATIC_DIR / "assets")), name="assets")

    @app.get("/")
    async def serve_index() -> FileResponse:
        return FileResponse(str(_INDEX_FILE))

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """API가 아닌 임의 경로는 SPA 진입점(index.html)으로 폴백."""
        # 존재하는 실제 파일이면 그대로 반환, 아니면 index.html
        candidate = _STATIC_DIR / full_path
        if candidate.is_file():
            return FileResponse(str(candidate))
        return FileResponse(str(_INDEX_FILE))

else:
    # 빌드 산출물이 아직 없을 때(개발 초기): API만 노출하고 안내 메시지 제공
    @app.get("/")
    async def root() -> JSONResponse:
        return JSONResponse(
            {
                "status": "healthy",
                "message": (
                    "Travel Mate Agent API가 실행 중입니다. "
                    "프론트엔드 빌드 결과가 backend/static에 없어 정적 서빙은 비활성화 상태입니다. "
                    "API는 /api/chat 으로 호출하세요."
                ),
            }
        )
