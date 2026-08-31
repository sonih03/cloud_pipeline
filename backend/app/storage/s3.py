import boto3
from botocore.exceptions import ClientError
from typing import Optional, List, Dict
from app.config import (
    AWS_REGION,
    AWS_S3_BUCKET_NAME,
    AWS_S3_IMAGES_PREFIX,
)

# 유효한 이미지 확장자 목록
VALID_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp')


class S3StorageManager:
    def __init__(self):
        self.bucket_name = AWS_S3_BUCKET_NAME
        self.region = AWS_REGION
        self.base_prefix = AWS_S3_IMAGES_PREFIX.strip("/")

        # EC2 IAM Role 자동 인증
        self.s3_client = boto3.client("s3", region_name=self.region)

    def _get_key(self, category: str, file_name: Optional[str] = None) -> str:
        """S3 Key 경로 생성"""
        category = category.strip("/")
        prefix = f"{self.base_prefix}/" if self.base_prefix else ""
        if file_name:
            return f"{prefix}{category}/{file_name.strip('/')}"
        return f"{prefix}{category}/"

    # ==========================================
    # 1. READ (조회 / 다운로드)
    # ==========================================
    def get_categories(self) -> List[str]:
        """S3에서 순수 음식 카테고리 폴더만 조회 (.DS_Store 등 숨김 폴더 제외)"""
        prefix = f"{self.base_prefix}/" if self.base_prefix else ""
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=prefix,
            Delimiter="/"
        )
        categories = []
        for p in response.get("CommonPrefixes", []):
            raw_prefix = p.get("Prefix", "")
            category_name = raw_prefix[len(prefix):].strip("/")
            # .DS_Store, __MACOSX, 숨김 폴더 필터링
            if category_name and not category_name.startswith(".") and category_name != "__MACOSX":
                categories.append(category_name)
        return sorted(categories)

    def list_category_images(self, category: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """카테고리 폴더 내의 유효한 이미지 파일 목록 및 S3 URL 반환"""
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
            # 숨김 파일 제외 및 이미지 확장자 검사
            if file_name.startswith(".") or not file_name.lower().endswith(VALID_IMAGE_EXTENSIONS):
                continue

            images.append({
                "category": category,
                "file_name": file_name,
                "image_url": self.get_public_url(category, file_name),
                "size": obj["Size"],
                "last_modified": obj["LastModified"].isoformat()
            })

            if limit and len(images) >= limit:
                break

        return images

    def get_public_url(self, category: str, file_name: str) -> str:
        """S3 퍼블릭 이미지 URL 생성"""
        key = self._get_key(category, file_name)
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"


# 싱글톤 인스턴스
s3_storage = S3StorageManager()