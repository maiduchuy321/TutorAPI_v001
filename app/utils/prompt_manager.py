from typing import Dict, List, Optional, Any
import json
import os
from pathlib import Path


class PromptManager:
    """
    Quản lý các prompt template dùng trong hệ thống chatbot
    """

    def __init__(self, prompts_dir: Optional[str] = None):
        """
        Khởi tạo PromptManager

        Args:
            prompts_dir: Đường dẫn đến thư mục chứa các file prompt JSON
                         Nếu không cung cấp, sẽ sử dụng thư mục mặc định là /app/prompts
        """
        if prompts_dir:
            self.prompts_dir = Path(prompts_dir)
        else:
            # Mặc định sẽ sử dụng thư mục /app/prompt
            self.prompts_dir = Path(__file__).parent.parent / "prompt"

        # Đảm bảo thư mục tồn tại
        os.makedirs(self.prompts_dir, exist_ok=True)

        # Tự động nạp các prompt template từ thư mục prompts
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Any]:
        """Nạp tất cả prompt templates từ thư mục prompts"""
        templates = {}
        for file_path in self.prompts_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    template_data = json.load(f)
                    template_name = file_path.stem  # Tên file không có phần mở rộng
                    templates[template_name] = template_data
            except Exception as e:
                print(f"Lỗi khi nạp prompt template từ {file_path}: {str(e)}")
        return templates

    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Lấy một template theo tên"""
        return self.templates.get(template_name)

    def format_system_message(self, template_name: str, **kwargs) -> Optional[str]:
        """
        Định dạng một system message dựa trên template và các tham số

        Args:
            template_name: Tên của template
            **kwargs: Các biến để thay thế trong template

        Returns:
            System message đã được định dạng hoặc None nếu template không tồn tại
        """
        template = self.get_template(template_name)
        if not template or "system_message" not in template:
            return None

        system_message = template["system_message"]

        # Thay thế các biến trong template
        for key, value in kwargs.items():
            placeholder = "{" + key + "}"
            system_message = system_message.replace(placeholder, str(value))

        return system_message

    def create_prompt_messages(self, template_name: str, user_message: str,
                               conversation_history: Optional[List[Dict[str, str]]] = None,
                               **kwargs) -> List[Dict[str, str]]:
        """
        Tạo danh sách các messages cho OpenAI API dựa trên template

        Args:
            template_name: Tên của template
            user_message: Tin nhắn của người dùng
            conversation_history: Lịch sử hội thoại (nếu có)
            **kwargs: Các biến để thay thế trong template

        Returns:
            Danh sách các messages cho OpenAI API
        """
        messages = []

        # Thêm system message nếu có template
        system_message = self.format_system_message(template_name, **kwargs)
        if system_message:
            messages.append({"role": "system", "content": system_message})

        # Thêm lịch sử hội thoại (nếu có)
        if conversation_history:
            messages.extend(conversation_history)

        # Thêm tin nhắn hiện tại của người dùng
        messages.append({"role": "user", "content": user_message})

        return messages

    def create_template(self, template_name: str, system_message: str,
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
        template_data = {
            "system_message": system_message,
        }

        if examples:
            template_data["examples"] = examples

        try:
            file_path = self.prompts_dir / f"{template_name}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)

            # Cập nhật cache
            self.templates[template_name] = template_data
            return True
        except Exception as e:
            print(f"Lỗi khi tạo prompt template {template_name}: {str(e)}")
            return False

    def update_template(self, template_name: str, system_message: Optional[str] = None,
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
        if template_name not in self.templates:
            return False

        template_data = self.templates[template_name].copy()

        if system_message is not None:
            template_data["system_message"] = system_message

        if examples is not None:
            template_data["examples"] = examples

        try:
            file_path = self.prompts_dir / f"{template_name}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)

            # Cập nhật cache
            self.templates[template_name] = template_data
            return True
        except Exception as e:
            print(f"Lỗi khi cập nhật prompt template {template_name}: {str(e)}")
            return False

    def delete_template(self, template_name: str) -> bool:
        """
        Xóa một prompt template

        Args:
            template_name: Tên của template

        Returns:
            True nếu xóa thành công, False nếu không
        """
        if template_name not in self.templates:
            return False

        try:
            file_path = self.prompts_dir / f"{template_name}.json"
            if file_path.exists():
                os.remove(file_path)

            # Xóa khỏi cache
            del self.templates[template_name]
            return True
        except Exception as e:
            print(f"Lỗi khi xóa prompt template {template_name}: {str(e)}")
            return False

    def list_templates(self) -> List[str]:
        """Liệt kê tên của tất cả template hiện có"""
        return list(self.templates.keys())