from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from datetime import datetime
from typing import Dict, List, Any

from app.controllers.lesson_controller import LessonController
from app.models.chat_model import ChatHistory
from sqlalchemy.orm import Session
from app.models.models import get_db, User
from app.schemas.theory import MessageRequest, MessageResponse, ChatHistoryResponse
from app.controllers.qa_message_controller import ChatSessionManager
from app.routers.lesson import get_lesson
from app.utils.reflection import Reflection
from app.config import REFLECTION
from app.prompt.theory_prompt import TheoryPrompt
router = APIRouter(
    prefix="/guide",
    tags=["guide"],
    responses={401: {"description": "Unauthorized"}},
)

chat_Session = ChatSessionManager()


def get_lesson_content_by_id(lesson_id, db):
    try:
        # Sử dụng trực tiếp LessonController
        lesson_controller = LessonController(db)
        lesson = lesson_controller.get_lesson(lesson_id)
        # print("Lesson", lesson)
        if lesson:
            # Lưu nội dung vào biến
            content = lesson.content
            return content
        else:
            print("Không tìm thấy bài giảng")
            return None
    except Exception as e:
        print(f"Lỗi: {e}")
        print("Không tồn tài bài giảng trong CSDL")
        return None



@router.post("/{session_id}", response_model=MessageResponse)
async def handle_message(session_id: str, message: MessageRequest, db: Session = Depends(get_db)):
    """
    Xử lý tin nhắn người dùng và trả về phản hồi từ LLM.

    Args:
        - **content**: Nội dung tin nhắn
        - **lesson_id**: ID của bài học muốn hỏi

    Returns:
        MessageResponse: Tin nhắn đã được tạo
    """

    start_time = datetime.now()
    # Kiểm tra lesson ID trước
    context = get_lesson_content_by_id(message.lesson_id, db)
    if context is None:
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        return MessageResponse(
            content="Không có ID bài giảng trong CSDL",
            processing_time=processing_time,
            timestamp=end_time
        )

    # Nếu có lesson ID hợp lệ, tiếp tục xử lý
    query = message.content
    response = chat_Session.progress_message(session_id, query)
    # Tính thời gian xử lý
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()

    return MessageResponse(
        content=response,
        processing_time=processing_time,
        timestamp=end_time
    )

@router.get("/{session_id}/history", response_model=ChatHistoryResponse)
async def get_history(session_id: str):
    """Lấy lịch sử chat"""
    chat_history = chat_Session.get_chat_history(session_id)
    return ChatHistoryResponse(messages=chat_history.get_history())