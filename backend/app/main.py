from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import Base, engine
from app.imageRag.web import router as image_rag_router
from app.auth.web import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 기동 시 PostgreSQL 테이블 자동 생성
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Korean Food Image RAG API",
    description="Food Image Classification using Gemini 3.6 Flash & S3 & PostgreSQL & Redis Auth",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(image_rag_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}