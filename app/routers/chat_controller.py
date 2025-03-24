from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from datetime import datetime
from typing import Dict, List, Any

from app.models.chat_model import ChatHistory
from app.schemas.responses import MessageRequest, MessageResponse, ChatHistoryResponse
from app.controllers.llm_service import generate_response, process_stream
from app.utils.reflection import Reflection
# from app.prompt import AITutorPrompt
from app.config import REFLECTION
from app.prompt.tutor_prompt import AITutorPrompt
router = APIRouter(
    prefix="/qa",
    tags=["chat"],
    responses={401: {"description": "Unauthorized"}},
)

# Lưu trữ chat history cho mỗi session
chat_sessions: Dict[str, ChatHistory] = {}


def get_chat_history(session_id: str) -> ChatHistory:
    """Lấy hoặc tạo mới chat history cho session"""
    if session_id not in chat_sessions:
        chat_sessions[session_id] = ChatHistory()
        # Thêm tin nhắn chào mừng
        chat_sessions[session_id].add_message(
            "Assistant",
            "💻 Học lập trình không khó! 🚀 Mình là gia sư AI, giúp bạn tiếp cận kiến thức lập trình một cách dễ hiểu và luôn sẵn sàng đồng hành cùng bạn trên hành trình khám phá công nghệ. 🤖"
        )
    return chat_sessions[session_id]


@router.post("/{session_id}", response_model=MessageResponse)
async def handle_message(session_id: str, message: MessageRequest):
    """
    Xử lý tin nhắn người dùng và trả về phản hồi từ LLM.

    Args:
        - **content**: Nội dung tin nhắn

    Returns:
        MessageResponse: Tin nhắn đã được tạo
    """
    start_time = datetime.now()
    query = message.content

    # Lấy chat history
    chat_history = get_chat_history(session_id)
    chat_history.add_message("user", query)

    # Tạo prompt
    history = chat_history.get_history()
    latest_history = REFLECTION(history, last_items_considered=8)
    prompt = AITutorPrompt(history=latest_history).format()

    # Gọi LLM API
    stream = generate_response(prompt)

    # Xử lý phản hồi
    response_text = ""
    response_text += process_stream(stream)


    # Cập nhật lịch sử
    chat_history.add_message("Assistant", response_text)

    # Tính thời gian xử lý
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()

    return MessageResponse(
        content=response_text,
        processing_time=processing_time,
        timestamp=end_time
    )

@router.get("/{session_id}/history", response_model=ChatHistoryResponse)
async def get_history(session_id: str):
    """
    Lấy chi tiết một cuộc hội thoại theo session_id.

    Args:
        - **session_id (int)**: ID cuộc hội thoại

    Returns:
        ConversationResponse: Chi tiết cuộc hội thoại
    """
    chat_history = get_chat_history(session_id)
    return ChatHistoryResponse(messages=chat_history.get_history())