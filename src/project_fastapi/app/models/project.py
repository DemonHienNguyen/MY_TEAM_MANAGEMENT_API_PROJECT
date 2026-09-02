from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class ProjectModel(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    create_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_delete: Mapped[bool] = mapped_column(Boolean, default=False)
    
    project_members = relationship("ProjectMemberModel", back_populates="project")
    tasks = relationship("TaskModel", back_populates="project")