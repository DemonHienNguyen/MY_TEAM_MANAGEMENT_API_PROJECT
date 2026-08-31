from ..db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, DateTime, ForeignKey, Enum, PrimaryKeyConstraint, Boolean
from datetime import datetime
import enum

class ProjectMemberRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"

class ProjectMemberModel(Base):
    __tablename__ = "project_members"
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    role: Mapped[str] = mapped_column(Enum(ProjectMemberRole), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_delete: Mapped[bool] = mapped_column(Boolean, default=False)
    
    user = relationship("UserModel", back_populates="project_members")
    project = relationship("ProjectModel", back_populates="project_members")
    __table_args__ = (
        PrimaryKeyConstraint("project_id", "user_id", name="pk_project_id_and_user_id"),
    )
    
    
    
    