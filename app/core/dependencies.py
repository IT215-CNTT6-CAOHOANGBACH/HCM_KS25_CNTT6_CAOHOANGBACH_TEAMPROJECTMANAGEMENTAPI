from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, ExpiredSignatureError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.user import User


bearer_scheme = HTTPBearer()


def get_current_user(
	credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
	db: Session = Depends(get_db),
) -> User:
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Token không hợp lệ",
		headers={"WWW-Authenticate": "Bearer"},
	)
	try:
		payload = jwt.decode(
			credentials.credentials,
			settings.SECRET_KEY,
			algorithms=[settings.ALGORITHM],
		)
		email = payload.get("sub")
		if not email:
			raise credentials_exception
	except ExpiredSignatureError:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token đã hết hạn",
			headers={"WWW-Authenticate": "Bearer"},
		)
	except JWTError:
		raise credentials_exception

	user = db.query(User).filter(User.email == email).first()
	if user is None:
		raise credentials_exception
	if not user.is_active:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Tài khoản không hoạt động",
		)
	return user


class RoleChecker:
	def __init__(self, allowed_roles: list[str]):
		self.allowed_roles = {role.upper() for role in allowed_roles}

	def __call__(self, current_user: User = Depends(get_current_user)) -> User:
		if current_user.role.upper() not in self.allowed_roles:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="Bạn không có quyền thực hiện thao tác này",
			)
		return current_user

