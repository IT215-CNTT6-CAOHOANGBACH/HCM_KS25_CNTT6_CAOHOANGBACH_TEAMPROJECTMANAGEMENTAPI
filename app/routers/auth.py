from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.database import get_db
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
	"/register",
	response_model=UserResponse,
	status_code=status.HTTP_201_CREATED,
	summary="Đăng ký tài khoản",
	description="Tạo tài khoản người dùng mới bằng email, họ tên và mật khẩu.",
	response_description="Thông tin tài khoản vừa đăng ký",
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
	return user_service.create_user(db, user_data)


@router.post(
	"/login",
	response_model=TokenResponse,
	status_code=status.HTTP_200_OK,
	summary="Đăng nhập",
	description="Xác thực thông tin đăng nhập và cấp JWT access token.",
	response_description="Access token dùng để gọi các API được bảo vệ",
)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
	user = user_service.authenticate_user(db, user_data)
	return {
     	"message":"Đăng nhập thành công",
		"access_token": create_access_token(
			{"sub": str(user.id), "email": user.email, "role": user.role}
		),
		"token_type": "bearer",
	}
