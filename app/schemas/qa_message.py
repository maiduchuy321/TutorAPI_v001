from pydantic import BaseModel
from typing import Optional

class QaRequest(BaseModel):
    lesson_id: str
    message: str

class QaResponse(BaseModel):
    message: str
    processing_time: Optional[float] = None




