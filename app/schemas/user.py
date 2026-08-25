from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=3, max_length=128)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Họ tên không được để trống")
        return value

class UserLogin(UserBase):
    password: str = Field(min_length=1, max_length=128)

class TokenResponse(BaseModel):
    message:str
    access_token: str
    token_type: str = "bearer"

class UserResponse(UserBase):
    id: int
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)