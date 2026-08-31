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
            print(f"[RAG] 카테고리 {len(self._cached_categories)}개 로드 완료: {self._cached_categories[:5]}", flush=True)
        return self._cached_categories

    def _optimize_image(self, image_bytes: bytes) -> bytes:
        """Gemini 전송용 JPEG 리사이징 (800px, 80% 품질)"""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.thumbnail((800, 800))
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=80)
            return buf.getvalue()
        except Exception:
            return image_bytes

    def _call_gemini_with_timeout(self, prompt: str, image_bytes: bytes) -> str:
        """Gemini API 호출 (최대 15초 제한 및 실패 시 1회 즉시 재시도)"""
        for attempt in range(1, 3):
            try:
                t0 = time.time()
                print(f"[RAG] Gemini 호출 시도 #{attempt} ({self.model_name})...", flush=True)
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                        prompt
                    ]
                )
                print(f"[RAG] Gemini 응답 성공! ({time.time() - t0:.2f}초 소요)", flush=True)
                return response.text or ""
            except Exception as e:
                print(f"[RAG] Gemini 호출 #{attempt} 실패: {str(e)}", flush=True)
                if attempt == 2:
                    raise e
                time.sleep(1)
        return ""

    def _sync_match_image(self, user_image_bytes: bytes, top_k_samples: int = 3) -> ImageMatchResponse:
        # 1. 카테고리 목록 확보
        categories = self._get_categories_cached()
        if not categories:
            raise Exception("S3 버킷에서 음식 카테고리 폴더를 찾을 수 없습니다.")

        # 2. 이미지 압축
        t_opt = time.time()
        optimized_bytes = self._optimize_image(user_image_bytes)
        print(f"[RAG] 이미지 최적화 완료: {len(user_image_bytes)} -> {len(optimized_bytes)} bytes ({time.time() - t_opt:.3f}초)",
              flush=True)

        # 3. Gemini 멀티모달 분석
        prompt = f"""
당신은 한국 음식 전문가 AI입니다.
제시된 사용자 음식 사진을 분석하여 아래 [후보 카테고리 목록] 중 가장 일치하거나 유사한 한국 음식을 하나 정확히 선택하세요.

[후보 카테고리 목록]
{', '.join(categories)}

출력 형식(반드시 이 형식을 엄격히 준수하세요):
카테고리: [선택한 카테고리 이름]
분석: [선택한 이유와 시각적 특징 2-3줄 서술]
"""
        text = self._call_gemini_with_timeout(prompt, optimized_bytes)

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

        # 5. S3에서 이미지 조회
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
        # 이벤트 루프 블로킹 방지를 위해 별도 스레드에서 최대 25초 제한으로 실행
        return await asyncio.wait_for(
            asyncio.to_thread(self._sync_match_image, user_image_bytes, top_k_samples),
            timeout=25.0
        )


image_rag_service = ImageRagService()