from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    category_id: Optional[int] = None
    name: str
    slug: str
    description: Optional[str] = None
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0, default=0)
    image: Optional[str] = None

class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    name: str
    slug: str
    description: Optional[str] = None
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0)
    image: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    category_id: Optional[int] = None
    name: str
    slug: str
    description: Optional[str] = None
    price: Decimal
    stock: int
    image: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
