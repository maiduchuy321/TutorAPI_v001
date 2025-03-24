# models.py - Định nghĩa các mô hình dữ liệu
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Message(BaseModel):
    role: str
    content: str

class ChatHistory(BaseModel):
    messages: List[Message] = []

class ChatRequest(BaseModel):
    message: str
    lesson: str

class ChatResponse(BaseModel):
    response: str