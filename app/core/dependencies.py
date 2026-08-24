from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.user import User
from app.utils.exceptions import (
    authentication_required,
    inactive_account,
    invalid_token,
    permission_denied,
    token_expired,
    user_not_found,
)

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise authentication_required()

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except ExpiredSignatureError:
        raise token_expired()
    except JWTError:
        raise invalid_token()

    subject = payload.get("sub")
    if subject is None:
        raise invalid_token()

    try:
        user_id = int(subject)
    except (TypeError, ValueError):
        user_id = None

    query = db.query(User)
    user = query.filter(User.id == user_id).first() if user_id is not None else query.filter(User.email == subject).first()
    if user is None:
        raise user_not_found()
    if not user.is_active:
        raise inactive_account()
    return user


class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = {role.upper() for role in allowed_roles}

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if (current_user.role or "").upper() not in self.allowed_roles:
            raise permission_denied()
        return current_user