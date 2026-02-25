"""Project schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
