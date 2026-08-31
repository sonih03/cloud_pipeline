from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.schema import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from app.auth.service import auth_service
from app.auth.deps import get_current_user
from app.auth.models import User

router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    return auth_service.register(req, db)


@router.post("/login", response_model=TokenResponse)
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(req, db)


@router.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    auth_service.logout(credentials.credentials)
    return {"message": "성공적으로 로그아웃되었습니다."}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user