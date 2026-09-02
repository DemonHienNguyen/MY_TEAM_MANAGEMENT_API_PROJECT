import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(Enum(UserRole), default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    project_members = relationship("ProjectMemberModel", back_populates="user")
    tasks = relationship("TaskModel", back_populates="user")
    attachments = relationship("AttachmentModel", back_populates="user")
    comments = relationship("CommnentModel", back_populates="user")