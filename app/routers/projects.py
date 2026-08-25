from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.project import Project, ProjectMember, ActivityLog
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectMemberCreate, ProjectUpdate, MemberResponse
router = APIRouter(
    prefix="/projects",
    tags =["Projects"]
)
# --- HÀM HELPER: Ghi log lịch sử ---
def log_activity(db: Session, project_id: int, user_id: int, action: str):
    log = ActivityLog(project_id=project_id, user_id=user_id, action=action)
    db.add(log)
    db.commit()
#--check dự án đó còn sự dụng dc ko--
def get_active_project(db: Session, project_id: int) -> Project:
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.is_deleted == False
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Dự án không tồn tại hoặc đã bị xóa")
    return project

# --- HÀM HELPER: Kiểm tra quyền OWNER ---
def check_is_owner(db: Session, project_id: int, user_id: int):
    get_active_project(db, project_id)
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
        ProjectMember.role == "OWNER"
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Chỉ OWNER mới có quyền thực hiện thao tác này")
    return member

#TẠO 1 DỰ ÁN VÀ PHÂN QUYỀN THÀNH OWNER
@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not project_in.name or len(project_in.name) > 20:
        raise HTTPException(status_code=400, detail="Tên dự án không được để trống và không vượt quá 20 ký tự")

    new_project = Project(name=project_in.name, description=project_in.description, owner_id=current_user.id)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    # Thêm user làm OWNER
    db.add(ProjectMember(project_id=new_project.id, user_id=current_user.id, role="OWNER"))
    db.commit()

    log_activity(db, new_project.id, current_user.id, "Tạo dự án mới")
    return new_project

#TÌM THEO TÊN chỉ có người trong dự án mới dc sự dụng
@router.get("", response_model=List[ProjectResponse])
def get_my_projects(
    search: Optional[str] = None, # Hỗ trợ Search theo tên
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    query = db.query(Project).join(ProjectMember).filter(
        ProjectMember.user_id == current_user.id,
        Project.is_deleted == False # KHÔNG lấy dự án đã xóa mềm
    )
    #nếu ko có sự dụng tham số seach thì ko chạy
    if search:
        query = query.filter(Project.name.ilike(f"%{search}%"))
    return query.all()

#TÌM THEO THAM SỐ ID NHẬP VÀO chỉ có người trong dự án mới dc sự dụng
@router.get("/{project_id}", response_model=ProjectResponse)
def get_project_detail(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = get_active_project(db, project_id)

    # Kiểm tra thành viên gồm kiểm tra những member == tham số id nhập vào và user hiện tại có ==  tham số nhập vào ko
    is_member = db.query(ProjectMember).filter(ProjectMember.project_id == project_id, ProjectMember.user_id == current_user.id).first()
    if not is_member:
        raise HTTPException(status_code=403, detail="Bạn không phải thành viên của dự án này")
    return project


#CẬP NHẬP
@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project_in: ProjectUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = get_active_project(db, project_id)
    
    check_is_owner(db, project_id, current_user.id)

    if project_in.name:
        project.name = project_in.name
    if project_in.description is not None:
        project.description = project_in.description

    db.commit()
    log_activity(db, project_id, current_user.id, "Cập nhật thông tin dự án")
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = get_active_project(db, project_id)
    
    check_is_owner(db, project_id, current_user.id)

    project.is_deleted = True # XÓA MỀM
    db.commit()
    log_activity(db, project_id, current_user.id, "Xóa dự án (Xóa mềm)")
    return None

# ==========================================
# CÁC API THÀNH VIÊN (MEMBERS)
# ==========================================

@router.get("/{project_id}/members", response_model=List[MemberResponse])
def get_project_members(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_active_project(db, project_id)
    # Phải là thành viên mới được xem danh sách
    is_member = db.query(ProjectMember).filter(ProjectMember.project_id == project_id, ProjectMember.user_id == current_user.id).first()
    if not is_member:
        raise HTTPException(status_code=403, detail="Bạn không có quyền truy cập")
    
    members = db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()
    return members


@router.post("/{project_id}/members", status_code=201)
def add_project_member(project_id: int, member_in: ProjectMemberCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_is_owner(db, project_id, current_user.id)
    get_active_project(db, project_id)
    existing = db.query(ProjectMember).filter(ProjectMember.project_id == project_id, ProjectMember.user_id == member_in.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Người dùng đã là thành viên của dự án")

    # Kiểm tra user có tồn tại trong hệ thống không
    user_exist = db.query(User).filter(User.id == member_in.user_id).first()
    if not user_exist:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại trong hệ thống")

    new_member = ProjectMember(project_id=project_id, user_id=member_in.user_id, role="MEMBER")
    db.add(new_member)
    db.commit()

    log_activity(db, project_id, current_user.id, f"Thêm user {member_in.user_id} vào dự án với vai trò MEMBER")
    return {"message": "Thêm thành viên thành công"}


@router.delete("/{project_id}/members/{user_id}", status_code=204)
def remove_project_member(project_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_is_owner(db, project_id, current_user.id)
    get_active_project(db, project_id)
    member_to_remove = db.query(ProjectMember).filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id).first()
    if not member_to_remove:
        raise HTTPException(status_code=404, detail="Thành viên không có trong dự án")

    # Không cho phép xóa bất kỳ OWNER nào
    if member_to_remove.role == "OWNER":
        raise HTTPException(status_code=400, detail="Không thể xóa thành viên có vai trò OWNER")

    db.delete(member_to_remove)
    db.commit()

    log_activity(db, project_id, current_user.id, f"Xóa user {user_id} khỏi dự án")
    return None