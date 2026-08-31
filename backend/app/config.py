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

# 이미지 디렉토리 자동 감지 (backend/images 또는 backend/images/images)
_raw_images_dir = BACKEND_DIR / "images"
if (_raw_images_dir / "images").exists():
    IMAGES_DIR = _raw_images_dir / "images"
else:
    IMAGES_DIR = _raw_images_dir

BASE_DIR = BACKEND_DIR

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-3.6-flash"