from app.models.chat_model import ChatHistory
from app.schemas.responses import MessageRequest, MessageResponse, ChatHistoryResponse
from app.controllers.llm_service import generate_response, process_stream
from app.utils.reflection import Reflection
from app.config import REFLECTION
from app.prompt.tutor_prompt import AITutorPrompt
from typing import Dict, List, Any

class ChatSessionManager:
    """Quản lý các phiên trò chuyện"""

    def __init__(self):
        self.chat_sessions: Dict[str, ChatHistory] = {}  # Lưu trữ chat history cho mỗi session
        self.messages: List[Dict[str, Any]] = []

    def add_message(self, role: str, content: str):
        """Thêm tin nhắn vào lịch sử"""
        self.messages.append({"role": role, "content": content})

    def get_history(self) -> List[Dict[str, Any]]:
        """Lấy toàn bộ lịch sử chat"""
        return self.messages

    def get_last_n_messages(self, n: int) -> List[Dict[str, Any]]:
        """Lấy n tin nhắn gần nhất"""
        return self.messages[-n:] if n < len(self.messages) else self.messages

    def get_chat_history(self, session_id: str) -> ChatHistory:
        """Lấy hoặc tạo mới lịch sử chat cho session"""
        if session_id not in self.chat_sessions:
            self.chat_sessions[session_id] = ChatHistory()
            # Thêm tin nhắn chào mừng
            self.chat_sessions[session_id].add_message(
                "Assistant",
                "💻 Chào mừng bạn đến với AI Gia sư! 🚀"
            )
        return self.chat_sessions[session_id]

    def progress_message(self, session_id: str, query: str) -> str:
        """Xử lý tin nhắn và phản hồi từ AI"""
        # Lấy chat history
        chat_history = self.get_chat_history(session_id)
        chat_history.add_message("user", query)

        # Tạo prompt
        history = chat_history.get_history()
        latest_history = REFLECTION(history, last_items_considered=12)
        prompt = AITutorPrompt(history=latest_history).format()

        # Gọi LLM API
        stream = generate_response(prompt)

        # Xử lý phản hồi
        response_text = process_stream(stream)

        # Cập nhật lịch sử
        chat_history.add_message("Assistant", response_text)

        return response_text
