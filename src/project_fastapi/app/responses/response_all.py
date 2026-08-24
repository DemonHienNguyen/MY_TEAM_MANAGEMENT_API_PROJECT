from pydantic import BaseModel, ConfigDict, Field
from typing import TypeVar, Generic, Any
from datetime import datetime, timezone

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    StatusCode: int 
    Message: str
    Error: str | list[dict[str, Any]] | None 
    Data: T 
    TimeStamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    Path: str 
    
    model_config = ConfigDict(
        from_attributes=True
    )    
    