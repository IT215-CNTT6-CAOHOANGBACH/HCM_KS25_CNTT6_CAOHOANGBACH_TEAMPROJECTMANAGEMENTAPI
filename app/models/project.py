from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.db.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    # THÊM: Tính năng xóa mềm
    is_deleted = Column(Boolean, default=False) 

class ProjectMember(Base):
    __tablename__ = "project_members"

    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(String(50), nullable=False)  # OWNER hoặc MEMBER
    joined_at = Column(DateTime, server_default=func.now(), nullable=False)

# THÊM BẢNG MỚI: Lưu lịch sử thao tác
class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(255), nullable=False) # Ví dụ: "Tạo dự án", "Xóa thành viên"...
    created_at = Column(DateTime, server_default=func.now(), nullable=False)