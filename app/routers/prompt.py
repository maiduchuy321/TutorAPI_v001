from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.models import get_db, User
from app.controllers.chatbot_controller import ChatbotController
from app.utils.auth import get_current_active_user
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/prompts",
    tags=["prompts"],
    responses={401: {"description": "Unauthorized"}},
)


class MessageExample(BaseModel):
    role: str
    content: str


class PromptTemplateCreate(BaseModel):
    template_name: str
    system_message: str
    examples: Optional[List[MessageExample]] = None


class PromptTemplateUpdate(BaseModel):
    system_message: Optional[str] = None
    examples: Optional[List[MessageExample]] = None


class PromptTemplateResponse(BaseModel):
    template_name: str
    system_message: str
    examples: Optional[List[MessageExample]] = None


@router.get("", response_model=List[str])
async def list_prompt_templates(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Lấy danh sách tất cả prompt templates"""
    chatbot_controller = ChatbotController(db)
    templates = await chatbot_controller.list_prompt_templates()
    return templates


@router.get("/{template_name}", response_model=PromptTemplateResponse)
async def get_prompt_template(
        template_name: str,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Lấy chi tiết của một prompt template"""
    chatbot_controller = ChatbotController(db)
    template = await chatbot_controller.get_prompt_template(template_name)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template '{template_name}' không tồn tại"
        )

    # Chuyển đổi dữ liệu template sang định dạng phản hồi
    response = {
        "template_name": template_name,
        "system_message": template.get("system_message", ""),
        "examples": template.get("examples", [])
    }

    return response


@router.post("", response_model=PromptTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt_template(
        template: PromptTemplateCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Tạo một prompt template mới"""
    chatbot_controller = ChatbotController(db)

    # Kiểm tra xem template đã tồn tại chưa
    existing_templates = await chatbot_controller.list_prompt_templates()
    if template.template_name in existing_templates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prompt template '{template.template_name}' đã tồn tại"
        )

    # Chuyển đổi từ Pydantic model sang dict
    examples = [example.model_dump() for example in template.examples] if template.examples else None

    # Tạo template mới
    success = await chatbot_controller.create_prompt_template(
        template.template_name,
        template.system_message,
        examples
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tạo prompt template"
        )

    # Trả về template đã tạo
    return {
        "template_name": template.template_name,
        "system_message": template.system_message,
        "examples": template.examples
    }


@router.put("/{template_name}", response_model=PromptTemplateResponse)
async def update_prompt_template(
        template_name: str,
        template: PromptTemplateUpdate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Cập nhật một prompt template"""
    chatbot_controller = ChatbotController(db)

    # Kiểm tra xem template có tồn tại không
    existing_template = await chatbot_controller.get_prompt_template(template_name)
    if not existing_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template '{template_name}' không tồn tại"
        )

    # Chuyển đổi từ Pydantic model sang dict
    examples = [example.model_dump() for example in template.examples] if template.examples else None

    # Cập nhật template
    success = await chatbot_controller.update_prompt_template(
        template_name,
        template.system_message,
        examples
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật prompt template"
        )

    # Lấy template đã cập nhật
    updated_template = await chatbot_controller.get_prompt_template(template_name)

    # Trả về template đã cập nhật
    return {
        "template_name": template_name,
        "system_message": updated_template.get("system_message", ""),
        "examples": updated_template.get("examples", [])
    }


@router.delete("/{template_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt_template(
        template_name: str,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Xóa một prompt template"""
    chatbot_controller = ChatbotController(db)

    # Kiểm tra xem template có tồn tại không
    existing_template = await chatbot_controller.get_prompt_template(template_name)
    if not existing_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template '{template_name}' không tồn tại"
        )

    # Xóa template
    success = await chatbot_controller.delete_prompt_template(template_name)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể xóa prompt template"
        )

    return None