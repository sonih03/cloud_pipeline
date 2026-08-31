from typing import List
from pydantic import BaseModel, Field


class RetrievedImageInfo(BaseModel):
    category: str
    image_path: str
    file_name: str

class MatchedImageItem(BaseModel):
    category: str
    file_name: str
    image_url: str

class ImageMatchResponse(BaseModel):
    predicted_category: str = Field(..., description="매칭된 가장 유사한 로컬 음식 카테고리")
    similarity_analysis: str = Field(..., description="업로드한 이미지와 해당 음식의 유사도 및 시각적 특징 분석")
    matched_images: List[RetrievedImageInfo] = Field(..., description="데이터셋에서 검색된 해당 카테고리의 대표 이미지 목록")