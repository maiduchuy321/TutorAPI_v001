# app/models/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Mapped, mapped_column
from datetime import datetime
from app.config import settings

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    qa_session = relationship("Qa_Session", back_populates="user")

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    qa_session = relationship("Qa_Session", back_populates="lesson")

    def __repr__(self):
        return f"<Lesson(id='{self.id}', title='{self.title}', content='{self.content}')>"

class Qa_Message(Base):
    __tablename__ = 'qa_messages'

    id = Column(Integer, primary_key=True)
    role = Column(String(20), nullable=False)  # 'user' hoặc 'assistant'
    content = Column(Text, nullable=False)
    session_id = Column(Integer, ForeignKey('qa_sessions.id'), nullable=False)

    # Relationships
    qa_session = relationship("Qa_Session", back_populates="qa_message")

    def __repr__(self):
        return f"<Message(session_id='{self.session_id}', role='{self.role}', content='{self.content[:20]}...')>"


class Qa_Session(Base):
    __tablename__ = 'qa_sessions'
    id = Column(String(100), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), nullable=False)
    histories = Column(Text, ForeignKey('qa_message.content'),nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    #Relationships
    user = relationship("User", back_populates="qa_session")
    lesson = relationship("Lesson", back_populates="qa_session")
    qa_message = relationship("Qa_Message", back_populates="qa_session")


# Engine và Session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Khởi tạo database
def init_db():
    Base.metadata.create_all(bind=engine)