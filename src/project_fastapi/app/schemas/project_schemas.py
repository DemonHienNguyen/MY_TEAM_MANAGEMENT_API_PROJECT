from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProjectInput(BaseModel):
    name: str = Field(...,min_length=1, max_length=50, examples=["Dự án VIP"])
    description: str = Field(default="", examples=["Dự án này làm những gì..."])
    @model_validator(mode="after")
    def check_due_date_after_created_at(self):
        if "test" in self.name.lower().strip():
            raise ValueError("Khong duoc chua tu 'test' trong ten du an")
        return self

class ProjectUpdate(BaseModel):
    name: str = Field(...,min_length=1, max_length=255, examples=["Dự án VIP"])
    description: str = Field(default="", max_length=500, examples=["Dự án này làm những gì..."])


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    # owner_id: int
    create_at: datetime
    is_delete: bool
    
    model_config = ConfigDict(
        from_attributes=True, str_strip_whitespace=True, extra="forbid"
    )
