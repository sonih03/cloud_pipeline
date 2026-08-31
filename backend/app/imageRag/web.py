from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from app.imageRag.schema import ImageMatchResponse
from app.imageRag.service import ImageRagService

router = APIRouter(prefix="/rag", tags=["Image RAG"])


def get_rag_service() -> ImageRagService:
    return ImageRagService()


@router.post(
    "/match-image",
    response_model=ImageMatchResponse,
    summary="음식 이미지 업로드 기반 유사 음식 매칭 및 분석"
)
async def match_food_image(
    file: UploadFile = File(..., description="비교할 음식 사진 파일 (jpg, png 등)"),
    top_k_samples: int = Form(default=3, description="반환할 매칭 폴더 내 대표 이미지 수"),
    service: ImageRagService = Depends(get_rag_service)
):
    # 파일 확장자 검증
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="지원하지 않는 이미지 형식입니다. (JPEG, PNG, WEBP만 가능)")

    try:
        image_bytes = await file.read()
        return await service.match_image_to_local_food(
            user_image_bytes=image_bytes,
            top_k_samples=top_k_samples
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))