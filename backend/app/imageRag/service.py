import io
import asyncio
from PIL import Image
from typing import List
from google import genai
from google.genai import types
from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.storage.s3 import s3_storage
from app.imageRag.schema import ImageMatchResponse, MatchedImageItem


class ImageRagService:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_name = GEMINI_MODEL
        self._cached_categories: List[str] = []

    def _get_categories_cached(self) -> List[str]:
        """S3 카테고리 목록을 메모리에 캐싱하여 매 요청마다 S3 조회하는 오버헤드 제거"""
        if not self._cached_categories:
            self._cached_categories = s3_storage.get_categories()
        return self._cached_categories

    def _optimize_image(self, image_bytes: bytes) -> Image.Image:
        """대용량 이미지를 800px로 빠르게 리사이징하여 메모리 상의 PIL 객체로 반환"""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.thumbnail((800, 800))
            return img
        except Exception:
            return Image.open(io.BytesIO(image_bytes))

    def _sync_match_image(self, user_image_bytes: bytes, top_k_samples: int = 3) -> ImageMatchResponse:
        """동기식 네트워크 및 AI 연산을 별도 스레드에서 고속 실행"""
        # 1. S3 카테고리 목록 조회
        categories = self._get_categories_cached()
        if not categories:
            raise Exception("S3 버킷에서 음식 카테고리 폴더를 찾을 수 없습니다.")

        # 2. 이미지 리사이징 (PIL 객체)
        pil_image = self._optimize_image(user_image_bytes)

        # 3. Gemini 멀티모달 분석
        prompt = f"""
당신은 한국 음식 전문가 AI입니다.
제시된 사용자 음식 사진을 분석하여 아래 [후보 카테고리 목록] 중 가장 일치하거나 유사한 한국 음식을 하나 정확히 선택하세요.
(만약 피자나 양식 등 목록에 없는 음식인 경우, 가장 형태나 색상이 유사한 한국 음식을 선택하세요)

[후보 카테고리 목록]
{', '.join(categories)}

출력 형식(반드시 이 형식을 엄격히 준수하세요):
카테고리: [선택한 카테고리 이름]
분석: [선택한 이유와 시각적 특징 2-3줄 서술]
"""

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[prompt, pil_image],
            config=types.GenerateContentConfig(
                temperature=0.2,
                top_p=0.8
            )
        )

        text = response.text or ""

        # 파싱 로직
        predicted_category = categories[0]
        analysis_text = text

        for line in text.splitlines():
            line_str = line.strip()
            if line_str.startswith("카테고리:"):
                cand = line_str.replace("카테고리:", "").strip()
                if cand in categories:
                    predicted_category = cand
            elif line_str.startswith("분석:"):
                analysis_text = line_str.replace("분석:", "").strip()

        # 4. S3에서 해당 카테고리의 대표 이미지 URL 리스트 가져오기
        s3_images = s3_storage.list_category_images(category=predicted_category, limit=top_k_samples)

        matched_items = [
            MatchedImageItem(
                category=img["category"],
                file_name=img["file_name"],
                image_url=img["image_url"]
            )
            for img in s3_images
        ]

        return ImageMatchResponse(
            predicted_category=predicted_category,
            similarity_analysis=analysis_text,
            matched_images=matched_items
        )

    async def match_image_to_local_food(self, user_image_bytes: bytes, top_k_samples: int = 3) -> ImageMatchResponse:
        # FastAPI의 비동기 루프를 차단하지 않도록 별도 워커 스레드로 분기
        return await asyncio.to_thread(self._sync_match_image, user_image_bytes, top_k_samples)


image_rag_service = ImageRagService()