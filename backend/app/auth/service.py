from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.auth.models import User
from app.auth.schema import UserRegisterRequest, UserLoginRequest, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.core.redis import redis_service


class AuthService:
    def register(self, req: UserRegisterRequest, db: Session) -> User:
        if db.query(User).filter(User.username == req.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 아이디입니다."
            )
        new_user = User(
            username=req.username,
            hashed_password=hash_password(req.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    def login(self, req: UserLoginRequest, db: Session) -> TokenResponse:
        user = db.query(User).filter(User.username == req.username).first()
        if not user or not verify_password(req.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="아이디 또는 비밀번호가 일치하지 않습니다."
            )

        token = create_access_token(data={"sub": user.username})
        return TokenResponse(access_token=token, username=user.username)

    def logout(self, token: str):
        redis_service.set_blacklist_token(token)


auth_service = AuthService()