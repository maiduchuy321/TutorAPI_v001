from dataclasses import Field

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.schemas.lesson import LessonBase


class Qa_SessionBase(BaseModel):
    user_id: int = Field(..., min_length=1)
    lesson_id: int = Field(..., min_length=1)

class Qa_SessionCreate(Qa_SessionBase):
    pass


class Qa_SessionResponese(Qa_SessionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class Qa_SessonDetail(Qa_SessionResponese):
    histories: List[Qa_SessionResponese] = []
