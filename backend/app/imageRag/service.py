import io
from PIL import Image
from google import genai
from google.genai import types
from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.storage.s3 import s3_storage
from app.imageRag.schema import ImageMatchResponse, MatchedImageItem


class ImageRagService:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_name = GEMINI_MODEL

    def _optimize_image(self, image_bytes: bytes) -> bytes:
        """이미지 리사이징 최적화"""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.thumbnail((1024, 1024))
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            return buf.getvalue()
        except Exception:
            return image_bytes

    async def match_image_to_local_food(self, user_image_bytes: bytes, top_k_samples: int = 3) -> ImageMatchResponse:
        # 1. S3에서 카테고리 목록 조회 (.DS_Store 등 제외됨)
        categories = s3_storage.get_categories()
        if not categories:
            raise Exception("S3 버킷에서 유효한 음식 카테고리 폴더를 찾을 수 없습니다.")

        # 2. 이미지 최적화
        optimized_bytes = self._optimize_image(user_image_bytes)

        # 3. Gemini 멀티모달 분석
        prompt = f"""
당신은 한국 음식 전문가 AI입니다.
제시된 사용자 음식 사진을 분석하여 아래 [후보 카테고리 목록] 중 가장 일치하는 음식 하나를 정확히 선택하세요.

[후보 카테고리 목록]
{', '.join(categories)}

출력 형식(반드시 이 형식을 엄격히 준수하세요):
카테고리: [선택한 카테고리 이름]
분석: [선택한 이유와 시각적 특징 2-3줄 서술]
"""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[
                types.Part.from_bytes(data=optimized_bytes, mime_type="image/jpeg"),
                prompt
            ]
        )

        text = response.text or ""

        # 파싱
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

        # 4. S3에서 이미지 URL 리스트 가져오기
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


image_rag_service = ImageRagService()