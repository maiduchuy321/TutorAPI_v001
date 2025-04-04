import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import conversation, prompt, auth, lesson, chat
from app.routers import chat_controller, chat_controller_qa
from app.models.models import init_db
from app.models.chat_model import ChatHistory


# Khởi tạo FastAPI
app = FastAPI(
    title="Chatbot AI System",
    description="API cho hệ thống chatbot AI sử dụng FastAPI và OpenAI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong thực tế, chỉ định cụ thể các nguồn được phép
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký routers
app.include_router(auth.router)
# app.include_router(chat.router)
# app.include_router(conversation.router)

app.include_router(chat_controller.router)
app.include_router(chat_controller_theory.router)
app.include_router(lesson.router)

# Khởi tạo database khi khởi động
@app.on_event("startup")
async def startup():
    init_db()

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Chào mừng đến với API Chatbot AI"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)