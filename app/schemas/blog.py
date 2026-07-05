from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BlogCreate(BaseModel):
    title: str
    slug: str
    content: str

class BlogUpdate(BaseModel):
    title: str
    slug: str
    content: str

class BlogResponse(BaseModel):
    id: int
    title: str
    slug: str
    content: str
    status: str
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
