from datetime import datetime
from typing import List, Dict, Any


class ChatHistory:
    def __init__(self):
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