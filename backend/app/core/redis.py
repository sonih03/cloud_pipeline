import redis
from app.config import REDIS_HOST, REDIS_PORT

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=True
)


class RedisService:
    @staticmethod
    def set_blacklist_token(token: str, expire_seconds: int = 86400):
        """로그아웃 시 JWT 토큰을 Redis 블랙리스트에 등록"""
        redis_client.setex(f"blacklist:{token}", expire_seconds, "revoked")

    @staticmethod
    def is_token_blacklisted(token: str) -> bool:
        """토큰이 블랙리스트에 있는지 확인"""
        return redis_client.exists(f"blacklist:{token}") > 0


redis_service = RedisService()