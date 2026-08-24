from fastapi import HTTPException, status


class ErrorMessage:
    EMAIL_ALREADY_EXISTS = "Email đã tồn tại"
    INVALID_CREDENTIALS = "Email hoặc mật khẩu không chính xác"
    ACCOUNT_INACTIVE = "Tài khoản đã bị vô hiệu hóa"
    INVALID_TOKEN = "Token không hợp lệ"
    TOKEN_EXPIRED = "Token đã hết hạn"
    AUTHENTICATION_REQUIRED = "Vui lòng đăng nhập để thực hiện chức năng này"
    PERMISSION_DENIED = "Bạn không có quyền thực hiện chức năng này"
    USER_NOT_FOUND = "Không tìm thấy người dùng"


def _authentication_error(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def email_already_exists() -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ErrorMessage.EMAIL_ALREADY_EXISTS)


def invalid_credentials() -> HTTPException:
    return _authentication_error(ErrorMessage.INVALID_CREDENTIALS)


def inactive_account() -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorMessage.ACCOUNT_INACTIVE)


def invalid_token() -> HTTPException:
    return _authentication_error(ErrorMessage.INVALID_TOKEN)


def token_expired() -> HTTPException:
    return _authentication_error(ErrorMessage.TOKEN_EXPIRED)


def authentication_required() -> HTTPException:
    return _authentication_error(ErrorMessage.AUTHENTICATION_REQUIRED)


def permission_denied() -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorMessage.PERMISSION_DENIED)


def user_not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorMessage.USER_NOT_FOUND)