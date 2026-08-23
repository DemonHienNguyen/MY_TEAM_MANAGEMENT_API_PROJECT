from ..db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from datetime import datetime

class CommnentModel(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("task.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    create_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    update_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    
    task = relationship("TaskModel", back_populates="comments")
    user = relationship("UserModel", back_populates="comments")