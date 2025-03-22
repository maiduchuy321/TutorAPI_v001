from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.models.models import get_db, User
from app.controllers.conversation_controller import ConversationController
from app.schemas.conversation import ConversationCreate, ConversationResponse, ConversationUpdate, ConversationDetail
from app.schemas.message import MessageResponse
from app.utils.auth import get_current_active_user

router = APIRouter(
    prefix="/api/qa/conversations",
    tags=["conversations"],
    responses={401: {"description": "Unauthorized"}},
)


@router.get("", response_model=List[ConversationResponse])
async def get_conversations(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    conversation_controller = ConversationController(db)
    conversations = conversation_controller.get_user_conversations(current_user.id)
    return conversations


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
        conversation: ConversationCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    conversation_controller = ConversationController(db)
    new_conversation = conversation_controller.create_conversation(current_user.id, conversation)
    return new_conversation


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
        conversation_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    conversation_controller = ConversationController(db)
    conversation = conversation_controller.get_conversation(conversation_id)

    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Lấy tin nhắn trong cuộc hội thoại
    messages = conversation_controller.get_messages(conversation_id)

    # Tạo đối tượng ConversationDetail
    return {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "title": conversation.title,
        "lesson_id": conversation.lesson_id,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "messages": messages
    }


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
        conversation_id: int,
        conversation_data: ConversationUpdate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    conversation_controller = ConversationController(db)

    # Kiểm tra quyền truy cập
    existing_conversation = conversation_controller.get_conversation(conversation_id)
    if not existing_conversation or existing_conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Cập nhật cuộc hội thoại
    updated_conversation = conversation_controller.update_conversation(conversation_id, conversation_data)
    return updated_conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
        conversation_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    conversation_controller = ConversationController(db)

    # Kiểm tra quyền truy cập
    existing_conversation = conversation_controller.get_conversation(conversation_id)
    if not existing_conversation or existing_conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Xóa cuộc hội thoại
    success = conversation_controller.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )

    return None


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
        conversation_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    conversation_controller = ConversationController(db)

    # Kiểm tra quyền truy cập
    conversation = conversation_controller.get_conversation(conversation_id)
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Lấy tin nhắn
    messages = conversation_controller.get_messages(conversation_id)
    return messages