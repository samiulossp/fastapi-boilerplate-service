from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    slug: str

class CategoryUpdate(BaseModel):
    name: str
    slug: str

class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
