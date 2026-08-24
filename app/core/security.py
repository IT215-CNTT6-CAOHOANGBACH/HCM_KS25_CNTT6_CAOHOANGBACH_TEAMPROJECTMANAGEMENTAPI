from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
	return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
	try:
		return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
	except (ValueError, TypeError):
		return False


def create_access_token(data: dict) -> str:
	payload = data.copy()
	payload["exp"] = datetime.now(timezone.utc) + timedelta(
		minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
	)
	return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
