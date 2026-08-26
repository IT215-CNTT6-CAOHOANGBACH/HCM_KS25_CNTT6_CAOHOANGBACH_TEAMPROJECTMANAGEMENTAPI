from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.project import ActivityLog, Project, ProjectMember
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectMemberCreate, ProjectUpdate


def log_activity(db: Session, project_id: int, user_id: int, action: str) -> None:
    log = ActivityLog(project_id=project_id, user_id=user_id, action=action)
    db.add(log)
    db.commit()


def get_active_project(db: Session, project_id: int) -> Project:
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.is_deleted == False,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Dự án không tồn tại hoặc đã bị xóa")
    return project


def check_is_owner(db: Session, project_id: int, user_id: int) -> ProjectMember:
    get_active_project(db, project_id)
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
        ProjectMember.role == "OWNER",
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Chỉ OWNER mới có quyền thực hiện thao tác này")
    return member


def create_project(db: Session, project_in: ProjectCreate, current_user: User) -> Project:
    if not project_in.name or len(project_in.name) > 10:
        raise HTTPException(status_code=400, detail="Tên dự án không được để trống và không vượt quá 20 ký tự")

    new_project = Project(
        name=project_in.name,
        description=project_in.description,
        owner_id=current_user.id,
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    db.add(ProjectMember(project_id=new_project.id, user_id=current_user.id, role="OWNER"))
    db.commit()
    log_activity(db, new_project.id, current_user.id, "Tạo dự án mới")
    return new_project


def list_my_projects(
    db: Session,
    current_user: User,
    search: Optional[str] = None,
) -> list[Project]:
    query = db.query(Project).join(ProjectMember).filter(
        ProjectMember.user_id == current_user.id,
        Project.is_deleted == False,
    )
    if search:
        query = query.filter(Project.name.ilike(f"%{search}%"))
    return query.all()


def get_project_detail(db: Session, project_id: int, current_user: User) -> Project:
    project = get_active_project(db, project_id)
    is_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id,
    ).first()
    if not is_member:
        raise HTTPException(status_code=403, detail="Bạn không phải thành viên của dự án này")
    return project


def update_project(
    db: Session,
    project_id: int,
    project_in: ProjectUpdate,
    current_user: User,
) -> Project:
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


def delete_project(db: Session, project_id: int, current_user: User) -> None:
    project = get_active_project(db, project_id)
    check_is_owner(db, project_id, current_user.id)
    project.is_deleted = True
    db.commit()
    log_activity(db, project_id, current_user.id, "Xóa dự án (Xóa mềm)")


def get_project_members(db: Session, project_id: int, current_user: User) -> list[ProjectMember]:
    get_active_project(db, project_id)
    is_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id,
    ).first()
    if not is_member:
        raise HTTPException(status_code=403, detail="Bạn không có quyền truy cập")
    return db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()


def add_project_member(
    db: Session,
    project_id: int,
    member_in: ProjectMemberCreate,
    current_user: User,
) -> dict[str, str]:
    check_is_owner(db, project_id, current_user.id)
    existing = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == member_in.user_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Người dùng đã là thành viên của dự án")
    user_exist = db.query(User).filter(User.id == member_in.user_id).first()
    if not user_exist:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại trong hệ thống")
    db.add(ProjectMember(project_id=project_id, user_id=member_in.user_id, role="MEMBER"))
    db.commit()
    log_activity(db, project_id, current_user.id, f"Thêm user {member_in.user_id} vào dự án với vai trò MEMBER")
    return {"message": "Thêm thành viên thành công"}


def remove_project_member(
    db: Session,
    project_id: int,
    user_id: int,
    current_user: User,
) -> None:
    check_is_owner(db, project_id, current_user.id)
    member_to_remove = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
    ).first()
    if not member_to_remove:
        raise HTTPException(status_code=404, detail="Thành viên không có trong dự án")
    if member_to_remove.role == "OWNER":
        raise HTTPException(status_code=400, detail="Không thể xóa thành viên có vai trò OWNER")
    db.delete(member_to_remove)
    db.commit()
    log_activity(db, project_id, current_user.id, f"Xóa user {user_id} khỏi dự án")