from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


# 단서 (Clues) 관련 스키마
class ClueStateElement(BaseModel):
    user_id: str
    clue_id: int
    interacted: bool

    class Config:
        from_attributes = True


class ClueListResponse(BaseModel):
    clues: List[ClueStateElement]


# 인물 상태 (Characters State) 관련 스키마
class CharacterStateElement(BaseModel):
    user_id: str
    character_id: int
    interacted: bool

    class Config:
        from_attributes = True


class CharacterListResponse(BaseModel):
    characters: List[CharacterStateElement]


# 인물 대화 (Messages) 관련 스키마
class ChatMessageCreate(BaseModel):
    content: str


class ChatMessageResponse(BaseModel):
    character_id: int
    content: str

    class Config:
        from_attributes = True


class ChatMessageElement(BaseModel):
    id: int
    user_id: str
    sender: str
    content: str
    created_at: datetime = Field(alias="createdAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class CharacterChatLogResponse(BaseModel):
    character_id: int
    messages: List[ChatMessageElement]


# 결과 제출 (Deductions) 관련 스키마
class DeductionRequest(BaseModel):
    content: str
    character: int
    clues: List[int]


class DeductionResponse(BaseModel):
    comment: str
    result: bool
