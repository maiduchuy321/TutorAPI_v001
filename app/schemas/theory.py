from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class MessageRequest(BaseModel):
    content: str
    lesson_id: int

class MessageResponse(BaseModel):
    content: str
    processing_time: Optional[float] = None
    timestamp: datetime = datetime.now()

class ChatHistoryResponse(BaseModel):
    messages: List[Dict[str, Any]]