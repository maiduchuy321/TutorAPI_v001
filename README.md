# Chatbot AI System với FastAPI

Hệ thống chatbot sử dụng core AI của OpenAI và server data PostgreSQL, được xây dựng với FastAPI và SQLAlchemy.

## Cấu trúc dự án

```
chatbot-ai-system/
├── app/                      # Thư mục chính của ứng dụng
│   ├── models/               # Định nghĩa dữ liệu (SQLAlchemy)
│   ├── controllers/          # Xử lý logic nghiệp vụ
│   ├── routers/              # API endpoints (FastAPI routers)
│   ├── schemas/              # Pydantic schemas
│   └── utils/                # Tiện ích
├── migrations/               # Database migrations
├── tests/                    # Unit tests
├── .env.example              # Mẫu file biến môi trường
├── docker-compose.yml        # Cấu hình Docker Compose
└── Dockerfile                # Cấu hình Docker
```

## Mô hình dữ liệu

Hệ thống gồm 4 model chính:
- **User**: Thông tin người dùng
- **Conversation**: Cuộc hội thoại
- **Message**: Tin nhắn trong cuộc hội thoại
- **Lesson**: Bài học liên kết với cuộc hội thoại

## Yêu cầu hệ thống

- Python 3.8+
- PostgreSQL
- Docker và Docker Compose (tùy chọn)

## Cài đặt và chạy

### Sử dụng Docker

1. Sao chép file `.env.example` thành `.env` và cấu hình các biến môi trường:

```bash
cp .env.example .env
nano .env  # Cấu hình biến môi trường
```

2. Khởi động các container với Docker Compose:

```bash
docker-compose up -d
```

Ứng dụng sẽ chạy tại http://localhost:8000

### Cài đặt thủ công

1. Tạo môi trường ảo:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Cài đặt các thư viện:

```bash
pip install -r requirements.txt
```

3. Cấu hình biến môi trường:

```bash
cp .env.example .env
nano .env  # Cấu hình biến môi trường
```

4. Khởi chạy ứng dụng:

```bash
uvicorn main:app --reload
```

## API Endpoints

### Xác thực
- `POST /api/auth/register` - Đăng ký người dùng mới
- `POST /api/auth/token` - Đăng nhập và nhận JWT token
- `GET /api/auth/me` - Lấy thông tin người dùng
- `PUT /api/auth/me` - Cập nhật thông tin người dùng

### Chat
- `POST /api/chat` - Gửi tin nhắn và nhận phản hồi từ AI

### Hội thoại
- `GET /api/conversations` - Lấy danh sách hội thoại
- `POST /api/conversations` - Tạo hội thoại mới
- `GET /api/conversations/{id}` - Lấy thông tin hội thoại
- `PUT /api/conversations/{id}` - Cập nhật hội thoại
- `DELETE /api/conversations/{id}` - Xóa hội thoại
- `GET /api/conversations/{id}/messages` - Lấy tin nhắn trong hội thoại

### Bài học
- `GET /api/lessons` - Lấy danh sách bài học
- `POST /api/lessons` - Tạo bài học mới
- `GET /api/lessons/{id}` - Lấy thông tin bài học
- `PUT /api/lessons/{id}` - Cập nhật bài học
- `DELETE /api/lessons/{id}` - Xóa bài học

## Tài liệu API

FastAPI tự động tạo tài liệu API sử dụng Swagger UI và ReDoc:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Ví dụ sử dụng API

### Đăng ký người dùng
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "email": "user1@example.com", "password": "password123"}'
```

### Đăng nhập
```bash
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user1&password=password123"
```

### Gửi tin nhắn
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "Xin chào, tôi muốn học về Python", "conversation_id": null, "lesson_id": null}'
```