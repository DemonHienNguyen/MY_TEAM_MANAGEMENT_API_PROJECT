from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone
from app.models import TaskStatus, TaskPriority
from typing import Literal
from .comment_schemas import CommentResponse
from .attachment_schemas import AttachmentResponse

class TaskInput(BaseModel):
    title: str = Field(..., examples=["Dự án làm game tai ương"])
    description: str = Field(default="")
    assignee_id: int = Field(..., examples=[2])
    status: Literal[TaskStatus.DONE, TaskStatus.IN_PROGRESS, TaskStatus.TODO] = Field(..., examples=[TaskStatus.DONE])
    priority: Literal[TaskPriority.HIGH, TaskPriority.LOW, TaskPriority.MEDIUM] = Field(..., examples=[TaskPriority.HIGH])
    due_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    create_at: datetime = Field(...)
    
class TaskUpdate(BaseModel):
    title: str = Field(..., examples=["Dự án làm game tai ương"])
    description: str = Field(default="")
    assignee_id: int = Field(..., examples=[2])
    status: Literal[TaskStatus.DONE, TaskStatus.IN_PROGRESS, TaskStatus.TODO] = Field(..., examples=[TaskStatus.DONE])
    priority: Literal[TaskPriority.HIGH, TaskPriority.LOW, TaskPriority.MEDIUM] = Field(..., examples=[TaskPriority.HIGH])
    due_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    create_at: datetime = Field(...)
    
class TaskResponse(BaseModel):
    id: int 
    project_id: int 
    title: str 
    description: str 
    assignee_id: int 
    status: str
    priority: str
    due_date: datetime 
    create_at: datetime 
    create_by: int
    
    
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid"
    )
        
class TaskResponseButForGetListTask(BaseModel):
    id: int 
    project_id: int
    title: str 
    description: str
    comments: list[CommentResponse]
    attachments: list[AttachmentResponse]
    assignee_id: int 
    status: str
    priority: str
    due_date: datetime 
    create_at: datetime 
    create_by: int
    
    
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid"
    )