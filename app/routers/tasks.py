from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import os, uuid, shutil

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.project import Project, ProjectMember
from app.models.task import Task, Comment, Attachment, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, CommentCreate, CommentResponse, AttachmentResponse

router = APIRouter(prefix="/projects", tags=["Tasks & Comments"])

# --- HELPER: Kiểm tra quyền trong Project ---
def get_member_role(db: Session, project_id: int, user_id: int):
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Bạn không phải thành viên của dự án này")
    return member.role

def check_assignee_in_project(db: Session, project_id: int, assignee_id: int):
    if not assignee_id: return
    exists = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == assignee_id
    ).first()
    if not exists:
        raise HTTPException(status_code=400, detail="Assignee không phải là thành viên của dự án")


# 1. TẠO & XEM DANH SÁCH TASK  Filter, Search)
@router.post("/{project_id}/tasks", response_model=TaskResponse, status_code=201 )
def create_task(project_id: int, task_in: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_member_role(db, project_id, current_user.id) # Bất kỳ member nào cũng được tạo task
    check_assignee_in_project(db, project_id, task_in.assignee_id)

    new_task = Task(**task_in.model_dump(), project_id=project_id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/{project_id}/tasks", response_model=List[TaskResponse])
def get_tasks(
    project_id: int,
    status: Optional[TaskStatus] = Query(None, description="Lọc theo TODO, IN_PROGRESS, DONE"),
    priority: Optional[TaskPriority] = Query(None, description="Lọc theo LOW, MEDIUM, HIGH"),
    assignee_id: Optional[int] = None,
    search: Optional[str] = Query(None, description="Tìm kiếm theo tiêu đề"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_member_role(db, project_id, current_user.id) # Kiểm tra quyền
    
    query = db.query(Task).filter(Task.project_id == project_id)

    if status: query = query.filter(Task.status == status)
    if priority: query = query.filter(Task.priority == priority)
    if assignee_id: query = query.filter(Task.assignee_id == assignee_id)
    if search: query = query.filter(Task.title.ilike(f"%{search}%"))

    return query.all()


# 2. CHI TIẾT, UPDATE, DELETE TASK
# (Đổi prefix riêng cho các API thao tác trực tiếp lên task_id)
task_router = APIRouter(prefix="/tasks", tags=["Tasks & Comments"])

@task_router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task: raise HTTPException(status_code=404, detail="Không tìm thấy task")
    
    get_member_role(db, task.project_id, current_user.id) # Chặn user khác project
    return task

@task_router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_in: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task: raise HTTPException(status_code=404, detail="Không tìm thấy task")
    
    role = get_member_role(db, task.project_id, current_user.id)
    
    # Phân quyền linh hoạt: Chỉ OWNER dự án hoặc chính Assignee của task đó mới được sửa
    if role != "OWNER" and task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="Chỉ Owner hoặc người được giao (Assignee) mới được sửa task")

    if task_in.assignee_id is not None:
        check_assignee_in_project(db, task.project_id, task_in.assignee_id)

    # Cập nhật không ghi đè: Chỉ lấy các trường user có gửi lên
    update_data = task_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task

@task_router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task: raise HTTPException(status_code=404, detail="Không tìm thấy task")
    
    role = get_member_role(db, task.project_id, current_user.id)
    if role != "OWNER": # Quy định: Chỉ Owner mới được xóa hẳn Task
        raise HTTPException(status_code=403, detail="Chỉ Owner mới có quyền xóa task")

    db.delete(task)
    db.commit()
    return None

# ==========================================
# 3. COMMENTS & FILE UPLOAD
# ==========================================
@task_router.post("/{task_id}/comments", response_model=CommentResponse)
def add_comment(task_id: int, comment_in: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task: raise HTTPException(status_code=404, detail="Không tìm thấy task")
    get_member_role(db, task.project_id, current_user.id)

    comment = Comment(task_id=task_id, user_id=current_user.id, content=comment_in.content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@task_router.post("/{task_id}/attachments", response_model=AttachmentResponse)
async def upload_file(task_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task: raise HTTPException(status_code=404, detail="Không tìm thấy task")
    get_member_role(db, task.project_id, current_user.id)

    # Validate file size (Limit ~ 5MB) và extension
    if file.size and file.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File quá lớn. Tối đa 5MB")
    
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ["jpg", "png", "pdf", "docx", "txt", "xlsx"]:
        raise HTTPException(status_code=400, detail="Định dạng file không được hỗ trợ")

    # Lưu file
    file_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    attachment = Attachment(task_id=task_id, uploader_id=current_user.id, file_name=file.filename, file_path=file_path)
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment