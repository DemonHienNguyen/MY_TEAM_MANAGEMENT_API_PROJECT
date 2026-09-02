from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..db import Base


class AttachmentModel(Base):
    __tablename__ = "attachments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(String(256), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("task.id", ondelete="CASCADE"), nullable=False)
    upload_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    create_at: Mapped[datetime] = mapped_column(DateTime, default= func.now())
    is_delete: Mapped[bool] = mapped_column(Boolean, default= False)
    
    user = relationship("UserModel", back_populates="attachments")
    task = relationship("TaskModel", back_populates="attachments")