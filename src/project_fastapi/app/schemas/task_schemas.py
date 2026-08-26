from pydantic import BaseModel, Field, ConfigDict, model_validator
from datetime import datetime, timezone
from ..models import TaskStatus, TaskPriority
from typing import Literal
from .comment_schemas import CommentResponse
from .attachment_schemas import AttachmentResponse

class TaskInput(BaseModel):
    title: str = Field(..., examples=["Dự án làm game tai ương"])
    description: str = Field(default="")
    assignee_id: int = Field(..., examples=[2])
    status: Literal[TaskStatus.DONE, TaskStatus.IN_PROGRESS, TaskStatus.TODO] = Field(..., examples=[TaskStatus.DONE])
    priority: Literal[TaskPriority.HIGH, TaskPriority.LOW, TaskPriority.MEDIUM] = Field(..., examples=[TaskPriority.HIGH])
    due_date: datetime | None = Field(default=None, examples=[None])
    create_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    @model_validator(mode="after")
    def check_due_date_after_created_at(self):
        if self.due_date is not None:
            due = self.due_date
            created = self.create_at
            if due.tzinfo is None:
                due = due.replace(tzinfo=timezone.utc)
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)

            if due <= created:
                raise ValueError("due_date phải diễn ra sau create_at!")

        return self
class TaskUpdate(BaseModel):
    title: str = Field(..., examples=["Dự án làm game tai ương"])
    description: str | None = Field(default=None, examples=[None])
    assignee_id: int = Field(..., examples=[2])
    status: Literal[TaskStatus.DONE, TaskStatus.IN_PROGRESS, TaskStatus.TODO] = Field(..., examples=[TaskStatus.DONE])
    priority: Literal[TaskPriority.HIGH, TaskPriority.LOW, TaskPriority.MEDIUM] = Field(..., examples=[TaskPriority.HIGH])
    due_date: datetime | None = Field(default= None, examples=[None])
    create_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @model_validator(mode="after")
    def check_due_date_after_created_at(self):
        if self.due_date is not None:
            due = self.due_date
            created = self.create_at
            if due.tzinfo is None:
                due = due.replace(tzinfo=timezone.utc)
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)

            if due <= created:
                raise ValueError("due_date phải diễn ra sau create_at!")

        return self
class TaskResponse(BaseModel):
    id: int 
    project_id: int 
    title: str 
    description: str | None
    assignee_id: int 
    status: str
    priority: str
    due_date: datetime | None
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