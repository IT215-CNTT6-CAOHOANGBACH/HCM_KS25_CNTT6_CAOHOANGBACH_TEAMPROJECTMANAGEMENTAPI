from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import RoleChecker, get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
	return current_user


@router.get("", response_model=list[UserResponse])
def read_users(
	search: str | None = Query(default=None, min_length=1),
	is_active: bool | None = None,
	db: Session = Depends(get_db),
	_: User = Depends(RoleChecker(["ADMIN"])),
):
	query = db.query(User)
	if search:
		pattern = f"%{search}%"
		query = query.filter((User.full_name.ilike(pattern)) | (User.email.ilike(pattern)))
	if is_active is not None:
		query = query.filter(User.is_active == is_active)
	return query.order_by(User.id).all()
