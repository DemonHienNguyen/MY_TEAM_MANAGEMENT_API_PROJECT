from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class CommentCreate(BaseModel):
    content: str = Field(default="")
    
class CommentResponse(BaseModel):
    id: int
    content: str
    task_id: int
    user_id: int
    create_at: datetime
    update_at: datetime
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid"
    )
        