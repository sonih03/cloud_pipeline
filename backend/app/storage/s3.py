import boto3
from botocore.exceptions import ClientError
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
        # "images/images" 경로 안전 처리
        self.base_prefix = AWS_S3_IMAGES_PREFIX.strip("/")

        # EC2 IAM Role 자동 인증 클라이언트
        self.s3_client = boto3.client("s3", region_name=self.region)

    def _get_key(self, category: str, file_name: Optional[str] = None) -> str:
        """S3 Key 경로 생성 (예: images/images/감자전/img_01.jpg)"""
        category = category.strip("/")
        prefix = f"{self.base_prefix}/" if self.base_prefix else ""
        if file_name:
            return f"{prefix}{category}/{file_name.strip('/')}"
        return f"{prefix}{category}/"

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """S3가 비공개 상태여도 브라우저가 사진을 볼 수 있도록 1시간 유효 서명 URL 발급"""
        try:
            return self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expires_in
            )
        except Exception:
            return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"

    # ==========================================
    # 1. READ (조회 / 서명 URL 발급)
    # ==========================================
    def get_categories(self) -> List[str]:
        """S3 images/images/ 하위 실제 음식 카테고리 목록 조회"""
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
            # .DS_Store, 임시 폴더 및 상위 폴더 필터링
            if cat and not cat.startswith(".") and cat not in ("__MACOSX", "images"):
                categories.append(cat)
        return sorted(categories)

    def list_category_images(self, category: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """선택된 음식 카테고리 내의 이미지 파일 목록 및 Pre-signed URL 반환"""
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

            images.append({
                "category": category,
                "file_name": file_name,
                "image_url": self.get_presigned_url(key),  # 서명된 URL 제공
                "size": obj["Size"],
                "last_modified": obj["LastModified"].isoformat()
            })

            if limit and len(images) >= limit:
                break

        return images


# 싱글톤 인스턴스
s3_storage = S3StorageManager()