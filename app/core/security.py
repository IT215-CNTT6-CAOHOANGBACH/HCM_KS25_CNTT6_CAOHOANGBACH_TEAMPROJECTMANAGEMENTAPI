from fastapi import HTTPException, status

def raise_not_found(detail: str = "Không tìm thấy tài nguyên"):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

def raise_bad_request(detail: str = "Yêu cầu không hợp lệ"):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

def raise_forbidden(detail: str = "Bạn không có quyền thực hiện thao tác này"):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)