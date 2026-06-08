"""
게임 코어 API 라우터.

대화 턴 진행(/chat)과 세션 초기화(/reset)를 제공한다.
턴 처리 파이프라인은 Orchestrator 에 위임한다.
"""

from fastapi import APIRouter

from app.schemas.request import ChatRequest
from app.schemas.response import TurnResult
from app.memory import store
from app.agents.orchestrator import Orchestrator

router = APIRouter()

_orchestrator = Orchestrator()


@router.post("/chat", response_model=TurnResult)
async def process_chat_turn(request: ChatRequest) -> TurnResult:
    """유저의 한 턴 입력을 받아 상태를 갱신하고 결과를 반환하는 코어 API."""
    return _orchestrator.run_turn(request)


@router.post("/reset/{session_id}")
async def reset_session(session_id: str) -> dict:
    """세션 상태를 초기화한다(게임 다시 시작)."""
    store.reset_session(session_id)
    return {"status": "ok", "message": f"세션 '{session_id}'이(가) 초기화되었습니다."}
