from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True
        
class ProjectMemberCreate(BaseModel):
    user_id: int
    
    
# Schema khi Sửa dự án (cho phép để trống)
class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# Schema trả về danh sách Member
class MemberResponse(BaseModel):
    project_id: int
    user_id: int
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True