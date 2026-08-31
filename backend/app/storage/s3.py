import boto3
from botocore.exceptions import ClientError
from typing import Optional, List, Dict
from app.config import (
    AWS_REGION,
    AWS_S3_BUCKET_NAME,
    AWS_S3_IMAGES_PREFIX,
)


class S3StorageManager:
    def __init__(self):
        self.bucket_name = AWS_S3_BUCKET_NAME
        self.region = AWS_REGION
        self.base_prefix = AWS_S3_IMAGES_PREFIX

        # EC2에 연결된 IAM Role(인스턴스 프로파일)을 통해 자동 인증
        self.s3_client = boto3.client("s3", region_name=self.region)

    def _get_key(self, category: str, file_name: Optional[str] = None) -> str:
        """S3 Key 경로 생성 (예: images/삼계탕/img_01.jpg)"""
        category = category.strip("/")
        if file_name:
            return f"{self.base_prefix}/{category}/{file_name.strip('/')}"
        return f"{self.base_prefix}/{category}/"

    # ==========================================
    # 1. READ (조회 / 다운로드)
    # ==========================================
    def get_categories(self) -> List[str]:
        """S3 images/ 하위 음식 카테고리 폴더 목록 조회"""
        prefix = f"{self.base_prefix}/"
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=prefix,
            Delimiter="/"
        )
        categories = []
        for p in response.get("CommonPrefixes", []):
            raw_prefix = p.get("Prefix", "")
            category_name = raw_prefix[len(prefix):].rstrip("/")
            if category_name:
                categories.append(category_name)
        return categories

    def list_category_images(self, category: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """선택 카테고리 폴더 내 이미지 목록 및 S3 URL 반환"""
        prefix = self._get_key(category)
        kwargs = {
            "Bucket": self.bucket_name,
            "Prefix": prefix
        }
        if limit:
            kwargs["MaxKeys"] = limit + 1

        response = self.s3_client.list_objects_v2(**kwargs)
        images = []

        for obj in response.get("Contents", []):
            key = obj["Key"]
            if key == prefix:
                continue

            file_name = key.split("/")[-1]
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

    def get_image_bytes(self, category: str, file_name: str) -> bytes:
        """S3에서 이미지 Raw Bytes 다운로드"""
        key = self._get_key(category, file_name)
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response["Body"].read()
        except ClientError as e:
            raise Exception(f"S3 다운로드 실패 ({key}): {str(e)}")

    def get_public_url(self, category: str, file_name: str) -> str:
        """S3 퍼블릭 이미지 URL 반환"""
        key = self._get_key(category, file_name)
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"

    # ==========================================
    # 2. CREATE & UPDATE (업로드 / 덮어쓰기)
    # ==========================================
    def upload_image(
        self,
        category: str,
        file_name: str,
        file_bytes: bytes,
        content_type: str = "image/jpeg"
    ) -> str:
        """S3 images/카테고리/ 경로에 이미지 파일 업로드"""
        key = self._get_key(category, file_name)
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_bytes,
                ContentType=content_type
            )
            return self.get_public_url(category, file_name)
        except ClientError as e:
            raise Exception(f"S3 업로드 실패 ({key}): {str(e)}")

    # ==========================================
    # 3. DELETE (삭제)
    # ==========================================
    def delete_image(self, category: str, file_name: str) -> bool:
        """단일 이미지 파일 삭제"""
        key = self._get_key(category, file_name)
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError as e:
            raise Exception(f"S3 파일 삭제 실패 ({key}): {str(e)}")

    def delete_category(self, category: str) -> bool:
        """카테고리 폴더 하위 파일 일괄 삭제"""
        prefix = self._get_key(category)
        try:
            paginator = self.s3_client.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                if "Contents" in page:
                    delete_keys = [{"Key": obj["Key"]} for obj in page["Contents"]]
                    self.s3_client.delete_objects(
                        Bucket=self.bucket_name,
                        Delete={"Objects": delete_keys}
                    )
            return True
        except ClientError as e:
            raise Exception(f"S3 카테고리 삭제 실패 ({category}): {str(e)}")


# 싱글톤 인스턴스
s3_storage = S3StorageManager()