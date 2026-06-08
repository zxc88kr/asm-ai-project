from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    session_id: str = Field(
        ..., 
        description="유저 세션 고유 ID (해당 유저의 단기 및 장기 기억 데이터를 불러오는 데 사용)"
    )
    user_message: str = Field(
        ..., 
        description="유저가 방금 입력한 채팅 텍스트"
    )
    current_chapter: int = Field(
        ..., 
        description="현재 프론트엔드에서 띄우고 있는 챕터 ID"
    )
    current_affinity: int = Field(
        ..., 
        description="현재까지 누적된 호감도 점수 (Agent의 톤 앤 매너 및 분기 결정에 사용)"
    )
