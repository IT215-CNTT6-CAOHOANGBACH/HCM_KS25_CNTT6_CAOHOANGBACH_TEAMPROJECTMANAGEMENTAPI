from fastapi import FastAPI
from app.db.database import engine, Base

from app.models.user import User
from app.models.project import Project, ProjectMember
from app.models.task import Task
from app.routers import auth, users, projects,tasks
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Project Management API")
#dk router
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
# app.include_router(tasks.router)

@app.get("/")
def health_check():
    return {"status": "success", "message": "API đang hoạt động tốt!"}

