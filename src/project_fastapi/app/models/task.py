from ..db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Text, ForeignKey, Enum, Boolean
from datetime import datetime
import enum

class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class TaskPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"    

class TaskModel(Base):
    __tablename__ = "task"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    assignee_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(Enum(TaskStatus), nullable=False)
    priority: Mapped[str] = mapped_column(Enum(TaskPriority), nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    create_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    create_by: Mapped[int] = mapped_column(Integer, nullable=False)
    is_delete: Mapped[bool] = mapped_column(Boolean, default= False)
    
    project = relationship("ProjectModel", back_populates="tasks")
    user = relationship("UserModel", back_populates="tasks")
    comments = relationship("CommnentModel", back_populates="task")
    attachments = relationship("AttachmentModel", back_populates="task")
    