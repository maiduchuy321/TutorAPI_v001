from typing import Optional, Dict, Any, List
import requests
from sqlalchemy.orm import Session
from app.controllers.conversation_controller import ConversationController
from app.controllers.lesson_controller import LessonController
from app.schemas.message import MessageCreate
from app.schemas.conversation import ConversationCreate
from app.config import settings
from app.utils.prompt_manager import PromptManager


class ChatbotController:
    def __init__(self, db: Session):
        self.db = db
        self.conversation_controller = ConversationController(db)
        self.lesson_controller = LessonController(db)
        self.api_key = settings.OPENAI_API_KEY
        self.api_url = settings.OPENAI_API_URL
        self.prompt_manager = PromptManager()

    async def process_message(self,
                              user_id: int,
                              message_content: str,
                              conversation_id: Optional[int] = None,
                              lesson_id: Optional[int] = None,
                              prompt_template: str = "default") -> Dict[str, Any]:
        """
        Xử lý tin nhắn từ người dùng và tạo phản hồi từ AI

        Args:
            user_id: ID của người dùng
            message_content: Nội dung tin nhắn
            conversation_id: ID cuộc hội thoại (nếu có)
            lesson_id: ID bài học (nếu có)
            prompt_template: Tên template prompt muốn sử dụng

        Returns:
            Dict chứa ID cuộc hội thoại và phản hồi từ AI
        """
        # Nếu không có conversation, tạo mới
        if not conversation_id:
            conversation_data = ConversationCreate(lesson_id=lesson_id)
            conversation = self.conversation_controller.create_conversation(user_id, conversation_data)
            conversation_id = conversation.id
        else:
            conversation = self.conversation_controller.get_conversation(conversation_id)
            if not conversation:
                conversation_data = ConversationCreate(lesson_id=lesson_id)
                conversation = self.conversation_controller.create_conversation(user_id, conversation_data)
                conversation_id = conversation.id

        # Lưu tin nhắn của người dùng
        user_message = MessageCreate(
            conversation_id=conversation_id,
            role="user",
            content=message_content
        )
        self.conversation_controller.add_message(user_message)

        # Lấy lịch sử hội thoại
        messages = self.conversation_controller.get_messages(conversation_id)
        conversation_history = [{"role": msg.role, "content": msg.content} for msg in messages]

        # Chuẩn bị prompt dựa vào template và ngữ cảnh
        lesson_title = ""
        lesson_content = ""

        if lesson_id:
            lesson = self.lesson_controller.get_lesson(lesson_id)
            if lesson:
                lesson_title = lesson.title
                lesson_content = lesson.content

                # Nếu có bài học, sử dụng template lesson
                if "lesson" in self.prompt_manager.list_templates():
                    prompt_template = "lesson"

        # Tạo messages cho OpenAI API
        openai_messages = self._prepare_messages(
            prompt_template,
            message_content,
            conversation_history[:-1],  # Bỏ tin nhắn cuối cùng vì đã được thêm vào bởi prompt_manager
            lesson_title=lesson_title,
            lesson_content=lesson_content
        )

        # Gọi OpenAI API
        try:
            endpoint = f"{self.api_url}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            payload = {
                "model": settings.OPENAI_MODEL,
                "messages": openai_messages,
                "temperature": 0.7,  # Có thể thêm vào settings
                "max_tokens": 800  # Có thể thêm vào settings
            }

            response = requests.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]

            # Lưu tin nhắn của assistant
            assistant_msg = MessageCreate(
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_message
            )
            self.conversation_controller.add_message(assistant_msg)

            return {
                "conversation_id": conversation_id,
                "response": assistant_message
            }
        except Exception as e:
            # Xử lý lỗi
            error_message = f"Lỗi khi gọi OpenAI API: {str(e)}"
            system_msg = MessageCreate(
                conversation_id=conversation_id,
                role="system",
                content=error_message
            )
            self.conversation_controller.add_message(system_msg)
            return {
                "conversation_id": conversation_id,
                "error": error_message
            }

    def _prepare_messages(self,
                          template_name: str,
                          user_message: str,
                          conversation_history: List[Dict[str, str]] = None,
                          **kwargs) -> List[Dict[str, str]]:
        """
        Chuẩn bị các messages cho OpenAI API sử dụng prompt template

        Args:
            template_name: Tên của template
            user_message: Tin nhắn của người dùng
            conversation_history: Lịch sử hội thoại
            **kwargs: Các tham số thay thế trong template

        Returns:
            Danh sách messages cho OpenAI API
        """
        # Nếu template không tồn tại, sử dụng default
        if template_name not in self.prompt_manager.list_templates():
            template_name = "default"

        # Tạo messages từ template
        return self.prompt_manager.create_prompt_messages(
            template_name,
            user_message,
            conversation_history,
            **kwargs
        )

    async def create_prompt_template(self,
                                     template_name: str,
                                     system_message: str,
                                     examples: Optional[List[Dict[str, str]]] = None) -> bool:
        """
        Tạo một prompt template mới

        Args:
            template_name: Tên của template
            system_message: System message mẫu
            examples: Các ví dụ few-shot (nếu có)

        Returns:
            True nếu tạo thành công, False nếu không
        """
        return self.prompt_manager.create_template(template_name, system_message, examples)

    async def update_prompt_template(self,
                                     template_name: str,
                                     system_message: Optional[str] = None,
                                     examples: Optional[List[Dict[str, str]]] = None) -> bool:
        """
        Cập nhật một prompt template

        Args:
            template_name: Tên của template
            system_message: System message mới (nếu có)
            examples: Các ví dụ few-shot mới (nếu có)

        Returns:
            True nếu cập nhật thành công, False nếu không
        """
        return self.prompt_manager.update_template(template_name, system_message, examples)

    async def delete_prompt_template(self, template_name: str) -> bool:
        """
        Xóa một prompt template

        Args:
            template_name: Tên của template

        Returns:
            True nếu xóa thành công, False nếu không
        """
        return self.prompt_manager.delete_template(template_name)

    async def list_prompt_templates(self) -> List[str]:
        """
        Liệt kê tất cả prompt templates

        Returns:
            Danh sách tên các template
        """
        return self.prompt_manager.list_templates()

    async def get_prompt_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Lấy chi tiết của một prompt template

        Args:
            template_name: Tên của template

        Returns:
            Chi tiết template hoặc None nếu không tồn tại
        """
        return self.prompt_manager.get_template(template_name)