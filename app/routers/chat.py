from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from sqlalchemy.orm import Session
from app.models.models import get_db, User
from app.controllers.chatbot_controller import ChatbotController
from app.schemas.message import ChatRequest, ChatResponse
from app.utils.auth import get_current_active_user

router = APIRouter(
    prefix="/api/qa",
    tags=["chat"],
    responses={401: {"description": "Unauthorized"}},
)


@router.post("", response_model=ChatResponse)
async def chat(
        chat_request: ChatRequest,
        prompt_template: Optional[str] = Query(None, description="Tên của prompt template muốn sử dụng"),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    if not chat_request.message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message is required"
        )

    chatbot_controller = ChatbotController(db)

    result = await chatbot_controller.process_message(
        current_user.id,
        chat_request.message,
        chat_request.conversation_id,
        chat_request.lesson_id,
        prompt_template or "default"  # Sử dụng template mặc định nếu không chỉ định
    )

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )

    return result