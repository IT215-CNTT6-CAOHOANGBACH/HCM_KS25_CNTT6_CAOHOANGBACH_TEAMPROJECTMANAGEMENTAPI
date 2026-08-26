from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import RoleChecker, get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.user_service import list_users

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
	"/me",
	response_model=UserResponse,
	summary="Xem hồ sơ hiện tại",
	description="Trả về thông tin của người dùng đang đăng nhập.",
	response_description="Hồ sơ người dùng hiện tại",
)
def get_profile(current_user: User = Depends(get_current_user)):
	return current_user


@router.get(
	"",
	response_model=list[UserResponse],
	summary="Danh sách người dùng",
	description="Admin xem danh sách người dùng với tìm kiếm, lọc trạng thái và phân trang.",
	response_description="Danh sách người dùng",
)
def get_users(
	search: str | None = Query(default=None, max_length=255),
	is_active: bool | None = None,
	page: int = Query(default=1, ge=1),
	limit: int = Query(default=10, ge=1, le=100),
	db: Session = Depends(get_db),
	current_user: User = Depends(RoleChecker(["ADMIN"])),
):
	return list_users(db, search, is_active, skip=(page - 1) * limit, limit=limit)
