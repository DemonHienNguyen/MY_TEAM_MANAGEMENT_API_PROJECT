from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ProjectInput(BaseModel):
    name: str = Field(...,min_length=1, max_length=255, examples=["Dự án VIP"])
    description: str = Field(default="", examples=["Dự án này làm những gì..."])


class ProjectUpdate(BaseModel):
    name: str = Field(...,min_length=1, max_length=255, examples=["Dự án VIP"])
    description: str = Field(default="", examples=["Dự án này làm những gì..."])


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    owner_id: int
    create_at: datetime
    is_delete: bool
    
    model_config = ConfigDict(
        from_attributes=True, str_strip_whitespace=True, extra="forbid"
    )
