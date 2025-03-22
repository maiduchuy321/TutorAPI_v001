from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.message import MessageResponse


class ConversationBase(BaseModel):
    title: Optional[str] = None
    lesson_id: Optional[int] = None


class ConversationCreate(ConversationBase):
    pass


class ConversationResponse(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    lesson_id: Optional[int] = None


class ConversationDetail(ConversationResponse):
    messages: List[MessageResponse] = []