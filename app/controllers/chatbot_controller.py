from typing import Optional, Dict, Any, List
import requests
from sqlalchemy.orm import Session
from app.controllers.conversation_controller import ConversationController
from app.controllers.lesson_controller import LessonController
from app.models.models import Message
from app.schemas.message import MessageCreate
from app.schemas.conversation import ConversationCreate, ConversationUpdate
from app.config import settings
from app.utils.prompt_manager import PromptManager

from langfuse.openai import OpenAI
from langfuse.decorators import observe
import os

os.environ["LANGFUSE_SECRET_KEY"]=settings.LANGFUSE_SECRET_KEY
os.environ["LANGFUSE_PUBLIC_KEY"]=settings.LANGFUSE_PUBLIC_KEY
os.environ["LANGFUSE_HOST"] = settings.LANGFUSE_HOST
# app/controllers/chatbot_controller.py
class ChatbotController:
    def __init__(self, db: Session):
        self.db = db
        self.conversation_controller = ConversationController(db)
        self.lesson_controller = LessonController(db)
        self.api_key = settings.OPENAI_API_KEY
        self.api_url = settings.OPENAI_API_URL
        self.prompt_manager = PromptManager()

    @observe()
    async def process_message(self, user_id: int, message_content: str,
                              conversation_id: Optional[int] = None,
                              lesson_id: Optional[int] = None,
                              prompt_template: str = "default") -> Dict[str, Any]:
        """
        Xử lý tin nhắn từ người dùng và tạo phản hồi từ LLM Instruct
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
        history = self.conversation_controller.get_messages(conversation_id)

        # Xây dựng prompt cho mô hình Instruct
        prompt = self._build_instruct_prompt(history, lesson_id, prompt_template)

        # Gọi API LLM
        try:
            endpoint = f"{self.api_url}/completions"  # Điều chỉnh URL endpoint theo API của bạn
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "model": settings.OPENAI_MODEL,
                "prompt": prompt,
                "max_tokens": 5000,
                "temperature": 0.5,
                "stop": ["<|eot_id|>"]  # Stop token phù hợp với định dạng
            }

            response = requests.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            assistant_message = result.get("choices", [{}])[0].get("text", "").strip()

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
            error_message = f"Lỗi khi gọi LLM API: {str(e)}"
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

    @observe()
    def _build_instruct_prompt(self, messages: List[Message], lesson_id: Optional[int] = None,
                               prompt_template: str = "default") -> str:
        """
        Xây dựng prompt cho mô hình LLaMa-3.3-70B-Instruct với định dạng mới
        """
        # Lấy system prompt từ template
        system_prompt = ""
        template = self.prompt_manager.get_template(prompt_template)
        if template and "system_message" in template:
            system_prompt = template["system_message"]

        # Thêm context từ bài học nếu có
        if lesson_id:
            lesson = self.lesson_controller.get_lesson(lesson_id)
            if lesson:
                lesson_context = f"\nBài học liên quan: {lesson.title}\n{lesson.content}\n"
                system_prompt += lesson_context

        # Xây dựng lịch sử trò chuyện
        history = ""
        for msg in messages:
            if msg.role == "user":
                history += f"<|eot_id|><|start_header_id|>user<|end_header_id|>\n{msg.content}\n"
            elif msg.role == "assistant":
                history += f"<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n{msg.content}\n"

        # Xây dựng prompt hoàn chỉnh theo định dạng mới
        full_prompt = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
        full_prompt += system_prompt
        full_prompt += "\n### **Conversation History:**\n"
        full_prompt += history
        full_prompt += "### **Response:**\n"

        # Thêm tin nhắn mới nhất của người dùng nếu cần
        if messages and messages[-1].role == "user":
            full_prompt += f"<|eot_id|><|start_header_id|>user<|end_header_id|>\n{messages[-1].content}\n"

        # Thêm token cho assistant để bắt đầu phản hồi
        full_prompt += "<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"

        return full_prompt

    # async def suggest_title(self, conversation_id: int) -> Optional[str]:
    #     """Đề xuất tiêu đề dựa trên nội dung trò chuyện"""
    #     conversation = self.conversation_controller.get_conversation(conversation_id)
    #     if not conversation:
    #         return None
    #
    #     messages = self.conversation_controller.get_messages(conversation_id)
    #     if len(messages) < 2:
    #         return None
    #
    #     user_message = next((msg for msg in messages if msg.role == "user"), None)
    #     if not user_message:
    #         return None
    #
    #     # Tạo prompt để gợi ý tiêu đề
    #     title_prompt = f"Hãy đề xuất một tiêu đề ngắn gọn (không quá 50 ký tự) cho cuộc trò chuyện bắt đầu với tin nhắn sau: '{user_message.content}'"
    #
    #     try:
    #         endpoint = f"{self.api_url}/completions"
    #         headers = {
    #             "Content-Type": "application/json",
    #             "Authorization": f"Bearer {self.api_key}"
    #         }
    #
    #         payload = {
    #             "model": settings.OPENAI_MODEL,
    #             "prompt": title_prompt,
    #             "max_tokens": 50,
    #             "temperature": 0.7
    #         }
    #
    #         response = requests.post(endpoint, headers=headers, json=payload)
    #         response.raise_for_status()
    #
    #         result = response.json()
    #         suggested_title = result.get("choices", [{}])[0].get("text", "").strip().strip('"')
    #
    #         if suggested_title:
    #             self.conversation_controller.update_conversation(
    #                 conversation_id,
    #                 ConversationUpdate(title=suggested_title)
    #             )
    #             return suggested_title
    #
    #     except Exception as e:
    #         print(f"Lỗi khi gợi ý tiêu đề: {str(e)}")
    #         return None
    @observe()
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

    @observe()
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

    @observe()
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

    @observe()
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