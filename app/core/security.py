import bcrypt
from jose import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

def hash_password(password: str, cost_factor: int = 12) -> str:
    """
    Băm mật khẩu sử dụng thư viện bcrypt trực tiếp.
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=cost_factor)
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Kiểm tra mật khẩu người dùng nhập vào có khớp với mật khẩu đã băm trong DB hay không.
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def create_access_token(data: dict) -> str:
    """
    Tạo Access Token (JWT) dựa trên thông tin payload (data) được truyền vào.
    """
    to_encode = data.copy()

    # Tính toán thời gian hết hạn (expiration time) - đọc từ config
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # Ký và tạo chuỗi token bằng thư viện PyJWT - đọc SECRET_KEY từ config
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt

