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
        # .env에서 전달받은 경로를 기준으로 고정 (예: images/images)
        self.base_prefix = AWS_S3_IMAGES_PREFIX.strip("/")

        # EC2 IAM Role 기반 S3 클라이언트
        self.s3_client = boto3.client("s3", region_name=self.region)

    def _get_key(self, category: str, file_name: Optional[str] = None) -> str:
        """S3 Key 경로 생성"""
        category = category.strip("/")
        prefix = f"{self.base_prefix}/" if self.base_prefix else ""
        if file_name:
            return f"{prefix}{category}/{file_name.strip('/')}"
        return f"{prefix}{category}/"

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """S3 Private 객체에 대한 1시간 유효 서명 URL 발급"""
        try:
            return self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expires_in
            )
        except Exception:
            return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"

    def get_categories(self) -> List[str]:
        """지정된 prefix 하위의 음식 카테고리 폴더 목록 조회"""
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
            # .DS_Store 및 시스템 임시 폴더 필터링
            if cat and not cat.startswith(".") and cat != "__MACOSX":
                categories.append(cat)
        return sorted(categories)

    def list_category_images(self, category: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """해당 카테고리의 이미지 파일 목록 및 Pre-signed URL 반환"""
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
                "image_url": self.get_presigned_url(key),
                "size": obj["Size"],
                "last_modified": obj["LastModified"].isoformat()
            })

            if limit and len(images) >= limit:
                break

        return images


# 싱글톤 인스턴스
s3_storage = S3StorageManager()