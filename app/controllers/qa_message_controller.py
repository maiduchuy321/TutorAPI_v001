from app.models.chat_model import ChatHistory
from app.schemas.responses import MessageRequest, MessageResponse, ChatHistoryResponse
from app.controllers.llm_service import generate_response, process_stream
from app.utils.reflection import Reflection
from app.config import REFLECTION
from app.prompt.tutor_prompt import AITutorPrompt
from typing import Dict, List, Any
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

def progress_message(session_id: str, query):
    # Lấy chat history
    chat_history = get_chat_history(session_id)
    chat_history.add_message("user", query)

    # Tạo prompt
    history = chat_history.get_history()
    latest_history = REFLECTION(history, last_items_considered=12)
    prompt = AITutorPrompt(history=latest_history).format()

    # Gọi LLM API
    stream = generate_response(prompt)

    # Xử lý phản hồi
    response_text = ""
    response_text += process_stream(stream)

    # Cập nhật lịch sử
    chat_history.add_message("Assistant", response_text)
