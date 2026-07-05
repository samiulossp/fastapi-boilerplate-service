from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.order import OrderResponse, OrderStatusUpdate
from app.services.order_service import (
    get_order,
    get_orders,
    place_order,
    update_order_status,
)

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("", response_model=OrderResponse, status_code=201)
def create(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return place_order(db, current_user)

@router.get("", response_model=List[OrderResponse])
def list_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_orders(db, current_user)

@router.get("/{order_id}", response_model=OrderResponse)
def detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_order(db, order_id, current_user)

@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_status(
    order_id: int,
    body: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_order_status(db, order_id, body.status, current_user)
