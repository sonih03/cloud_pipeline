FROM python:3.12-slim

WORKDIR /app

# 시스템 필수 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 의존성 복사 및 설치
COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt

# 소스코드 전체 복사
COPY . .

EXPOSE 8000

# FastAPI 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]