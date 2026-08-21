from fastapi import FastAPI
from app.db.database import engine, Base

# Import bắt buộc tất cả models để Base nhận diện được schema
from app.models.user import User
from app.models.project import Project, ProjectMember
from app.models.task import Task

# Lệnh tự động tạo tất cả các bảng trong MySQL nếu chưa tồn tại
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Project Management API")

@app.get("/")
def health_check():
    return {"status": "success", "message": "API đang hoạt động tốt!"}