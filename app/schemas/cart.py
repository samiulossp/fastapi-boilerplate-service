from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, default=1)

class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: Decimal
    product_image: Optional[str] = None
    quantity: int
    subtotal: Decimal

class CartResponse(BaseModel):
    id: int
    items: List[CartItemResponse]
    total: Decimal
