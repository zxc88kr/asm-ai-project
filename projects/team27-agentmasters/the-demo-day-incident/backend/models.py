from sqlalchemy import Column, Integer, Boolean, Text, DateTime
from sqlalchemy.sql import func
from database import Base


# 단서 확인 여부 테이블
class ClueState(Base):
    __tablename__ = "clue_state"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Text, index=True, nullable=False)  # 사용자 식별을 위한 UUID
    clue_id = Column(Integer, index=True, nullable=False)
    interacted = Column(Boolean, default=True, nullable=False)


# 인물 카드 확인 여부 테이블
class CharacterState(Base):
    __tablename__ = "character_state"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Text, index=True, nullable=False)  # 사용자 식별을 위한 UUID
    character_id = Column(Integer, index=True, nullable=False)
    interacted = Column(Boolean, default=True, nullable=False)


# 인물과의 대화 기록 테이블
class ChatMessage(Base):
    __tablename__ = "chat_message"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Text, index=True, nullable=False)  # 사용자 식별을 위한 UUID
    sender = Column(Text, nullable=False)
    character_id = Column(Integer, index=True, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
