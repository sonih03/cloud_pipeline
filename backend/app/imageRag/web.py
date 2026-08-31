import urllib.parse
from fastapi import APIRouter, UploadFile, File, Query, HTTPException, Depends
from fastapi.responses import Response
from app.imageRag.service import image_rag_service
from app.storage.s3 import s3_storage
from app.imageRag.schema import ImageMatchResponse
from app.auth.deps import get_current_user
from app.auth.models import User

router = APIRouter(prefix="/rag", tags=["Image RAG"])


@router.post("/match-image", response_model=ImageMatchResponse)
async def match_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)  # 로그인 필수 가드
):
    user_image_bytes = await file.read()
    return await image_rag_service.match_image_to_local_food(user_image_bytes)


@router.get("/image")
async def get_food_image(category: str = Query(...), file_name: str = Query(...)):
    """S3 이미지 스트리밍 (퍼블릭 조회용)"""
    try:
        decoded_category = urllib.parse.unquote(category)
        decoded_file_name = urllib.parse.unquote(file_name)

        image_bytes = s3_storage.get_image_bytes(decoded_category, decoded_file_name)
        ext = decoded_file_name.lower().split(".")[-1]
        media_type = f"image/{ext}" if ext in ["png", "jpeg", "webp", "gif"] else "image/jpeg"

        return Response(
            content=image_bytes,
            media_type=media_type,
            headers={
                "Cache-Control": "public, max-age=86400",
                "Content-Type": media_type
            }
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"S3 이미지 로드 실패: {str(e)}")