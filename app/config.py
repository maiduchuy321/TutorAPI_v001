import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Cấu hình ứng dụng sử dụng Pydantic"""
    # Database
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql://username:password@localhost/chatbot_db")

    # JWT
    JWT_SECRET: str = os.environ.get("JWT_SECRET")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MINUTES: int = 60 * 24  # 24 giờ

    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.environ.get("OPENAI_API_KEY")
    OPENAI_MODEL: str = "LLama-3.3-70B-Instruct"
    OPENAI_API_URL: str = os.environ.get("FPT_API_URL", "https://api.fpt.ai/nlp/llm/api/v1")


    LANGFUSE_SECRET_KEY : Optional[str] = os.environ.get("LANGFUSE_SECRET_KEY")
    LANGFUSE_PUBLIC_KEY : Optional[str] = os.environ.get("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_HOST : str = os.environ.get("LANGFUSE_HOST")

    # Ứng dụng
    APP_NAME: str = "Chatbot AI System"
    APP_VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Thêm dòng này để cho phép các biến "extra"

# Khởi tạo settings
settings = Settings()