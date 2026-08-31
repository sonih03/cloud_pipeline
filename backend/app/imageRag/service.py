import io
import time
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
        if not self._cached_categories:
            print("[RAG] S3 카테고리 목록 최초 조회...", flush=True)
            self._cached_categories = s3_storage.get_categories()
            print(f"[RAG] 카테고리 {len(self._cached_categories)}개 로드 완료", flush=True)
        return self._cached_categories

    def _optimize_image(self, image_bytes: bytes) -> bytes:
        """Gemini 전송 속도를 위한 600px 경량화"""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.thumbnail((600, 600))
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=75)
            return buf.getvalue()
        except Exception:
            return image_bytes

    def _sync_match_image(self, user_image_bytes: bytes, top_k_samples: int = 3) -> ImageMatchResponse:
        # 1. S3 카테고리 목록 로드
        categories = self._get_categories_cached()
        if not categories:
            raise Exception("S3 버킷에서 음식 카테고리 폴더를 찾을 수 없습니다.")

        # 2. 이미지 압축
        optimized_bytes = self._optimize_image(user_image_bytes)

        # 3. Gemini 멀티모달 분석
        prompt = f"""
당신은 음식 분류 전문가 AI입니다.
제시된 사용자 음식 사진을 분석하여 아래 [후보 카테고리 목록] 중 가장 일치하거나 유사한 음식을 하나 선택하세요.

[후보 카테고리 목록]
{', '.join(categories)}

출력 형식(반드시 이 형식을 엄격히 지키고 불필요한 서술은 생략하세요):
카테고리: [선택한 카테고리 이름]
분석: [선택한 이유와 시각적 특징 1-2줄]
"""
        t0 = time.time()
        print(f"[RAG] Gemini 호출 시작 ({self.model_name})...", flush=True)

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[
                types.Part.from_bytes(data=optimized_bytes, mime_type="image/jpeg"),
                prompt
            ],
            config=types.GenerateContentConfig(
                max_output_tokens=200,  # 긴 응답 방지로 생성 속도 5배 향상
                temperature=0.2
            )
        )
        print(f"[RAG] Gemini 응답 성공! ({time.time() - t0:.2f}초 소요)", flush=True)

        text = response.text or ""

        # 4. 결과 파싱
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

        print(f"[RAG] 매칭된 카테고리: '{predicted_category}'", flush=True)

        # 5. S3에서 해당 카테고리 이미지 목록 가져오기
        s3_images = s3_storage.list_category_images(category=predicted_category, limit=top_k_samples)

        matched_items = [
            MatchedImageItem(
                category=img["category"],
                file_name=img["file_name"],
                image_url=img["image_url"]
            )
            for img in s3_images
        ]
        print(f"[RAG] S3 매칭 이미지 {len(matched_items)}건 전송 완료", flush=True)

        return ImageMatchResponse(
            predicted_category=predicted_category,
            similarity_analysis=analysis_text,
            matched_images=matched_items
        )

    async def match_image_to_local_food(self, user_image_bytes: bytes, top_k_samples: int = 3) -> ImageMatchResponse:
        # 인공적인 타임아웃 제한 제거: 안전하게 백그라운드 스레드에서 끝까지 실행
        return await asyncio.to_thread(self._sync_match_image, user_image_bytes, top_k_samples)


image_rag_service = ImageRagService()