from pydantic import BaseModel, Field
from typing import Dict, Any, List, Literal

class TurnResult(BaseModel):
    next_chapter: int= Field(
        default=None,
        description="전환될 챕터 ID"
    )
    affinity_delta: int = Field(
        default=0, 
        description="이번 턴의 호감도 증감치 (예: +2, -1 등. 프론트엔드 게이지 애니메이션용)"
    )
    agent_dialogue_list: List[str]= Field(
        default_factory=list,
        description="유저에게 보여질 캐릭터의 응답"
    )
    emotion_code: Literal["idle", "smile", "sad", "surprise"] = Field(
        default="idle",
        description="렌더링할 표정 코드 (예: 'idle', 'smile', 'sad', 'surprise')"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="도구 호출 결과, 씬 전환의 이유 등 형태가 유동적인 추가 정보"
    )