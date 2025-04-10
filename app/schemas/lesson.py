from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LessonBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    content: str


class LessonCreate(LessonBase):
    id: Optional[int] = None  # id là tùy chọn, có thể có hoặc không


class LessonResponse(LessonBase):
    id: int
    created_at: datetime
    updated_at: datetime
    content: str

    class Config:
        from_attributes = True


class LessonUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    content: Optional[str] = None