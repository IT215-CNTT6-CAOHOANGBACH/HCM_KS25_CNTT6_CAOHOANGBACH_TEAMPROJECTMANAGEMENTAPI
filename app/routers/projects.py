from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectMemberCreate, ProjectUpdate, MemberResponse
from app.services import project_service
router = APIRouter(
    prefix="/projects",
    tags =["Projects"]
)
#TẠO 1 DỰ ÁN VÀ PHÂN QUYỀN THÀNH OWNER
@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return project_service.create_project(db, project_in, current_user)

#TÌM THEO TÊN chỉ có người trong dự án mới dc sự dụng
@router.get("", response_model=List[ProjectResponse])
def get_my_projects(
    search: Optional[str] = None, # Hỗ trợ Search theo tên
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return project_service.list_my_projects(db, current_user, search)

#TÌM THEO THAM SỐ ID NHẬP VÀO chỉ có người trong dự án mới dc sự dụng
@router.get("/{project_id}", response_model=ProjectResponse)
def get_project_detail(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return project_service.get_project_detail(db, project_id, current_user)


#CẬP NHẬP
@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project_in: ProjectUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return project_service.update_project(db, project_id, project_in, current_user)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project_service.delete_project(db, project_id, current_user)
    return None

# ==========================================
# CÁC API THÀNH VIÊN (MEMBERS)
# ==========================================

@router.get("/{project_id}/members", response_model=List[MemberResponse])
def get_project_members(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return project_service.get_project_members(db, project_id, current_user)


@router.post("/{project_id}/members", status_code=201)
def add_project_member(project_id: int, member_in: ProjectMemberCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return project_service.add_project_member(db, project_id, member_in, current_user)


@router.delete("/{project_id}/members/{user_id}", status_code=204)
def remove_project_member(project_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project_service.remove_project_member(db, project_id, user_id, current_user)
    return None