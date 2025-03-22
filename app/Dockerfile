# Sử dụng Python 3.10 làm base image
FROM python:3.10-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các dependency cần thiết
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code
COPY . .

# Mở port mà ứng dụng sẽ chạy trên đó
EXPOSE 8000

# Chạy ứng dụng khi container được khởi động
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]