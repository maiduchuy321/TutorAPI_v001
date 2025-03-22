from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from app.models.models import Conversation, Message
from app.schemas.conversation import ConversationCreate, ConversationUpdate
from app.schemas.message import MessageCreate


class ConversationController:
    def __init__(self, db: Session):
        self.db = db

    def create_conversation(self, user_id: int, data: ConversationCreate):
        conversation = Conversation(
            user_id=user_id,
            title=data.title or f"Conversation {datetime.utcnow()}",
            lesson_id=data.lesson_id
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_conversation(self, conversation_id: int):
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def get_user_conversations(self, user_id: int) -> List[Conversation]:
        return self.db.query(Conversation).filter(Conversation.user_id == user_id).order_by(
            Conversation.updated_at.desc()).all()

    def update_conversation(self, conversation_id: int, data: ConversationUpdate):
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None

        if data.title is not None:
            conversation.title = data.title
        if data.lesson_id is not None:
            conversation.lesson_id = data.lesson_id

        conversation.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def delete_conversation(self, conversation_id: int):
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False

        self.db.delete(conversation)
        self.db.commit()
        return True

    def add_message(self, data: MessageCreate):
        message = Message(
            conversation_id=data.conversation_id,
            role=data.role,
            content=data.content
        )
        self.db.add(message)

        # Update conversation timestamp
        conversation = self.get_conversation(data.conversation_id)
        conversation.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(message)
        return message

    def get_messages(self, conversation_id: int) -> List[Message]:
        return self.db.query(Message).filter(Message.conversation_id == conversation_id).order_by(
            Message.created_at).all()