from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AttachmentResponse(BaseModel):
    id:int
    filename: str
    file_path: str
    file_type: str
    file_size: int
    task_id:int
    upload_by: int
    create_at: datetime 
    
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid"
    )
    