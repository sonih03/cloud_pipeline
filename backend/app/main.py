from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import IMAGES_DIR
from app.imageRag.web import router as image_rag_router

app = FastAPI(
    title="Food Image RAG API",
    description="Gemini 기반 한식 이미지 RAG API",
    version="1.0.0"
)

# 1. CORS 허용 Origin 목록 설정
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# 2. CORS 미들웨어 등록
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 허용할 출처 목록 (개발 시 "*"로 전체 허용도 가능)
    allow_credentials=True,     # 쿠키 및 인증 헤더 포함 허용
    allow_methods=["*"],        # 모든 HTTP 메서드 허용 (GET, POST, OPTIONS 등)
    allow_headers=["*"],        # 모든 HTTP 헤더 허용
)

# 정적 파일 마운트
if IMAGES_DIR.exists():
    app.mount("/static/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")

# 라우터 등록
app.include_router(image_rag_router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "Food Image RAG API"}