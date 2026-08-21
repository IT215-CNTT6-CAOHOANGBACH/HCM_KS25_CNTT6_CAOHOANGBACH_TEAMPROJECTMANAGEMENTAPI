from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "MEDIUM"
    status: Optional[str] = "TODO"

class TaskCreate(TaskBase):
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None

class TaskResponse(TaskBase):
    id: int
    project_id: int
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True