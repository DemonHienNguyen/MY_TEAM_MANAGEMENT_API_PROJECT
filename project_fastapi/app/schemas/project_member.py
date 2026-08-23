from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Literal
from app.models import ProjectMemberRole
from .user_schemas import UserResponseButForGetProjectMember

class ProjectMemberInput(BaseModel):
    user_id: int = Field(...)
    role: Literal[ProjectMemberRole.MEMBER, ProjectMemberRole.OWNER] = Field(
        default=ProjectMemberRole.MEMBER
    )
    join_at: datetime = Field(default_factory=lambda: datetime.now())


class ProjectMemberOutput(BaseModel):
    project_id: int 
    user_id: int 
    role: Literal[ProjectMemberRole.MEMBER, ProjectMemberRole.OWNER] 
    joined_at: datetime 

    model_config = ConfigDict(
        from_attributes=True, str_strip_whitespace=True, extra="forbid"
    )

class ProjectMemberOutputButForGetMember(BaseModel):
    project_id: int 
    user: UserResponseButForGetProjectMember
    role: Literal[ProjectMemberRole.MEMBER, ProjectMemberRole.OWNER] 
    joined_at: datetime 

    model_config = ConfigDict(
        from_attributes=True, str_strip_whitespace=True, extra="forbid"
    )
