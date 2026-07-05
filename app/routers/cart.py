from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse
from app.services.cart_service import (
    add_to_cart,
    clear_cart,
    get_cart,
    remove_cart_item,
    update_cart_item,
)

router = APIRouter(prefix="/cart", tags=["cart"])

@router.get("", response_model=CartResponse)
def get(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_cart(db, current_user)

@router.post("/items", response_model=CartResponse, status_code=201)
def add_item(
    body: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return add_to_cart(db, body, current_user)

@router.put("/items/{item_id}", response_model=CartResponse)
def update_item(
    item_id: int,
    body: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_cart_item(db, item_id, body, current_user)

@router.delete("/items/{item_id}", response_model=CartResponse)
def remove_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return remove_cart_item(db, item_id, current_user)

@router.delete("", response_model=CartResponse)
def clear(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return clear_cart(db, current_user)
