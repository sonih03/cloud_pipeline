import os
from pathlib import Path
from dotenv import load_dotenv

# 디렉토리 경로 정의
APP_DIR = Path(__file__).resolve().parent          # .../backend/app
BACKEND_DIR = APP_DIR.parent                      # .../backend
PROJECT_ROOT = BACKEND_DIR.parent                 # .../project

# .env 탐색 및 로드 (최상위 project/.env 우선 탐색)
if (PROJECT_ROOT / ".env").exists():
    load_dotenv(PROJECT_ROOT / ".env")
elif (BACKEND_DIR / ".env").exists():
    load_dotenv(BACKEND_DIR / ".env")
else:
    load_dotenv()

# 로컬 이미지 디렉토리 감지 (로컬 참조/임시 저장용)
_raw_images_dir = BACKEND_DIR / "images"
if (_raw_images_dir / "images").exists():
    IMAGES_DIR = _raw_images_dir / "images"
else:
    IMAGES_DIR = _raw_images_dir

BASE_DIR = BACKEND_DIR

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

# AWS S3 설정 (.env 미설정 시 기본값 자동 적용)
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME", "qwe-s3-resource")
AWS_S3_IMAGES_PREFIX = os.getenv("AWS_S3_IMAGES_PREFIX", "images").strip("/")