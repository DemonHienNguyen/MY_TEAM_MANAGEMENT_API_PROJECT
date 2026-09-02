from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    StatusCode: int 
    Message: str
    Error: str | list[dict[str, Any]] | None 
    Data: T 
    TimeStamp: datetime | str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    Path: str 
    
    model_config = ConfigDict(
        from_attributes=True
    )    
    