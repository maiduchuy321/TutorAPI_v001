from typing import List, Dict, Any


class Reflection:
    """
    Trích xuất n tin nhắn gần nhất từ lịch sử chat.
    """

    def __call__(self, chat_history: List[Dict[str, Any]], last_items_considered: int = 12) -> List[Dict[str, Any]]:
        """
        Trích xuất tin nhắn gần nhất từ lịch sử chat.

        Args:
            chat_history: Danh sách tin nhắn chat.
            last_items_considered: Số lượng tin nhắn gần nhất cần giữ lại.

        Returns:
            Lịch sử chat được cắt ngắn chỉ chứa tin nhắn gần nhất.
        """
        return chat_history[-last_items_considered:] if last_items_considered < len(chat_history) else chat_history