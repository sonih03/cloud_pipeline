import urllib.parse
import boto3
from typing import Optional, List, Dict
from app.config import (
    AWS_REGION,
    AWS_S3_BUCKET_NAME,
    AWS_S3_IMAGES_PREFIX,
)

VALID_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp')


class S3StorageManager:
    def __init__(self):
        self.bucket_name = AWS_S3_BUCKET_NAME
        self.region = AWS_REGION
        self.base_prefix = AWS_S3_IMAGES_PREFIX.strip("/")
        self.s3_client = boto3.client("s3", region_name=self.region)

    def _get_key(self, category: str, file_name: Optional[str] = None) -> str:
        """S3 Key 경로 생성 (예: images/images/피자/Img_027_0001.jpg)"""
        category = category.strip("/")
        prefix = f"{self.base_prefix}/" if self.base_prefix else ""
        if file_name:
            return f"{prefix}{category}/{file_name.strip('/')}"
        return f"{prefix}{category}/"

    def get_categories(self) -> List[str]:
        """S3에서 실제 음식 카테고리 폴더 목록 조회"""
        prefix = f"{self.base_prefix}/" if self.base_prefix else ""
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=prefix,
            Delimiter="/"
        )
        categories = []
        for p in response.get("CommonPrefixes", []):
            raw_prefix = p.get("Prefix", "")
            cat = raw_prefix[len(prefix):].strip("/")
            if cat and not cat.startswith(".") and cat != "__MACOSX":
                categories.append(cat)
        return sorted(categories)

    def list_category_images(self, category: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """선택 카테고리 폴더 내 이미지 목록 및 안전하게 URL 인코딩된 스트리밍 URL 반환"""
        prefix = self._get_key(category)
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=prefix
        )
        images = []

        for obj in response.get("Contents", []):
            key = obj["Key"]
            if key == prefix:
                continue

            file_name = key.split("/")[-1]
            if file_name.startswith(".") or not file_name.lower().endswith(VALID_IMAGE_EXTENSIONS):
                continue

            # 한글 카테고리 및 파일명을 안전한 RFC 표준 URL 형태로 인코딩
            encoded_category = urllib.parse.quote(category)
            encoded_file_name = urllib.parse.quote(file_name)
            image_url = f"/rag/image?category={encoded_category}&file_name={encoded_file_name}"

            images.append({
                "category": category,
                "file_name": file_name,
                "image_url": image_url,
                "size": obj["Size"],
                "last_modified": obj["LastModified"].isoformat()
            })

            if limit and len(images) >= limit:
                break

        return images

    def get_image_bytes(self, category: str, file_name: str) -> bytes:
        """S3에서 원본 이미지 바이트 데이터 다운로드"""
        key = self._get_key(category, file_name)
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
        return response["Body"].read()


s3_storage = S3StorageManager()