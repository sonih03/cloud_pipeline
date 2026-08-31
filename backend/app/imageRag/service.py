import io
from pathlib import Path
from typing import List, Tuple
from PIL import Image
from google import genai
from google.genai import types
from pydantic import BaseModel

from app.config import GEMINI_API_KEY, GEMINI_MODEL, IMAGES_DIR, BASE_DIR
from app.imageRag.schema import RetrievedImageInfo, ImageMatchResponse


# Gemini 구조화된 출력(Structured Output)용 스키마
class CategoryMatchResult(BaseModel):
    best_category: str
    analysis: str


class ImageRagService:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY를 찾을 수 없습니다. 루트 .env 파일을 확인해 주세요.")

        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_name = GEMINI_MODEL
        self.images_root = IMAGES_DIR

    def _get_available_categories(self) -> List[str]:
        """로컬 images 폴더 내 존재하는 음식 디렉토리 목록 조회"""
        if not self.images_root.exists():
            return []
        return [d.name for d in self.images_root.iterdir() if d.is_dir()]

    def _get_category_sample_images(self, category: str, limit: int = 3) -> List[Path]:
        """매칭된 카테고리 폴더에서 대표 이미지 추출"""
        cat_dir = self.images_root / category
        if not cat_dir.exists():
            return []

        valid_extensions = ("*.jpg", "*.jpeg", "*.png", "*.webp")
        found_files = []
        for ext in valid_extensions:
            found_files.extend(list(cat_dir.glob(ext)))
            if len(found_files) >= limit:
                break
        return found_files[:limit]

    async def match_image_to_local_food(self, user_image_bytes: bytes, top_k_samples: int = 3) -> ImageMatchResponse:
        categories = self._get_available_categories()
        if not categories:
            raise ValueError("로컬 images 디렉토리에서 음식 카테고리 폴더를 찾을 수 없습니다.")

        # 1. 업로드된 바이트를 PIL Image로 변환
        user_image = Image.open(io.BytesIO(user_image_bytes)).convert("RGB")

        # 2. Gemini 멀티모달 분석: 업로드된 사진과 가장 일치하는 카테고리 선정
        prompt = f"""
당신은 한식 및 요리 이미지 분석 전문가입니다.
사용자가 업로드한 이미지를 정밀 분석하고, 아래 [보유 음식 카테고리 목록] 중 가장 시각적/재료적으로 일치하거나 유사한 음식을 정확히 1개 선정하세요.

[보유 음식 카테고리 목록]:
{', '.join(categories)}

- best_category: 위 목록에 존재하는 정확한 카테고리 이름 (목록에 없는 단어 사용 금지)
- analysis: 업로드된 음식의 색감, 주재료, 조리 형태, 플레이팅 등을 근거로 왜 해당 음식과 가장 유사한지 전문가 관점에서 상세하고 친절하게 설명
"""

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[prompt, user_image],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=CategoryMatchResult,
                temperature=0.2
            )
        )

        result_data: CategoryMatchResult = response.parsed
        matched_cat = result_data.best_category.strip()

        # 3. 매칭된 카테고리 폴더에서 로컬 이미지 파일 검색 (Retrieval)
        sample_paths = self._get_category_sample_images(matched_cat, limit=top_k_samples)

        matched_image_infos: List[RetrievedImageInfo] = []
        for img_path in sample_paths:
            try:
                rel_path = str(img_path.relative_to(BASE_DIR)).replace("\\", "/")
            except ValueError:
                rel_path = str(img_path)

            matched_image_infos.append(
                RetrievedImageInfo(
                    category=matched_cat,
                    image_path=rel_path,
                    file_name=img_path.name
                )
            )

        return ImageMatchResponse(
            predicted_category=matched_cat,
            similarity_analysis=result_data.analysis,
            matched_images=matched_image_infos
        )