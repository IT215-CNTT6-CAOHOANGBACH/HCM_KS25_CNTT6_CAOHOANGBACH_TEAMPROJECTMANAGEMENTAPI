from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.utils.exceptions import email_already_exists, inactive_account, invalid_credentials


def create_user(db: Session, user_data: UserCreate) -> User:
    email = str(user_data.email).lower()
    if db.query(User).filter(User.email == email).first():
        raise email_already_exists()

    user = User(
        email=email,
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),
        role="USER",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, user_data: UserLogin) -> User:
    user = db.query(User).filter(User.email == user_data.email).first()
    if user is None or not verify_password(user_data.password, user.password_hash):
        raise invalid_credentials()
    if not user.is_active:
        raise inactive_account()
    return user


def list_users(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
    skip: int = 0,
    limit: int = 10,
) -> list[User]:
    query = db.query(User)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter((User.email.ilike(pattern)) | (User.full_name.ilike(pattern)))
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    return query.order_by(User.id).offset(skip).limit(limit).all()