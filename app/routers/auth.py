from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.user_service import authenticate_user, create_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
	return create_user(db, user_data)


@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
	user = authenticate_user(db, user_data)
	return {
		"access_token": create_access_token(
			{"sub": user.email, "user_id": user.id, "role": user.role}
		),
		"token_type": "bearer",
	}
