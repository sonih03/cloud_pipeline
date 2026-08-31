from pydantic import BaseModel
from typing import List


class MatchedImageItem(BaseModel):
    category: str
    file_name: str
    image_url: str


# 기존 web.py 호환용 별칭
class RetrievedImageInfo(MatchedImageItem):
    pass


class ImageMatchResponse(BaseModel):
    predicted_category: str
    similarity_analysis: str
    matched_images: List[MatchedImageItem]