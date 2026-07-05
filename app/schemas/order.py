from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class OrderItemResponse(BaseModel):
    id: int
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    quantity: int
    unit_price: Decimal

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: Decimal
    status: str
    items: List[OrderItemResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class OrderStatusUpdate(BaseModel):
    status: str
