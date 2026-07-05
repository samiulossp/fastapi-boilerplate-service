from decimal import Decimal
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.user import User
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderResponse, OrderItemResponse


VALID_STATUSES = {"pending", "paid", "processing", "shipped", "delivered", "cancelled"}


def _get_repo(db: Session) -> OrderRepository:
    return OrderRepository(db)


def _build_order_response(order: Order) -> OrderResponse:
    items = []
    for item in order.items:
        items.append(
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.name if item.product else None,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
        )
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        total_amount=order.total_amount,
        status=order.status,
        items=items,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


def place_order(db: Session, current_user: User) -> OrderResponse:
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty",
        )

    total = Decimal("0.00")
    order_items_data = []

    for cart_item in cart.items:
        product = db.query(Product).filter(Product.id == cart_item.product_id).first()
        if not product or product.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{cart_item.product.name if cart_item.product else 'unknown'}' is not available",
            )
        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for '{product.name}'. Available: {product.stock}",
            )

        line_total = product.price * cart_item.quantity
        total += line_total
        order_items_data.append(
            {
                "product_id": product.id,
                "quantity": cart_item.quantity,
                "unit_price": product.price,
            }
        )

    order = Order(user_id=current_user.id, total_amount=total, status="pending")
    db.add(order)
    db.flush()

    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data["product_id"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
        )
        db.add(order_item)

        product = db.query(Product).filter(Product.id == item_data["product_id"]).first()
        product.stock -= item_data["quantity"]

    for cart_item in cart.items:
        db.delete(cart_item)
    db.commit()
    db.refresh(order)
    return _build_order_response(order)


def get_orders(db: Session, current_user: User) -> List[OrderResponse]:
    repo = _get_repo(db)
    is_admin = current_user.is_admin
    user_id = None if is_admin else current_user.id
    orders = repo.get_all(user_id=user_id, is_admin=is_admin)
    return [_build_order_response(o) for o in orders]


def get_order(db: Session, order_id: int, current_user: User) -> OrderResponse:
    repo = _get_repo(db)
    order = repo.get_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this order",
        )
    return _build_order_response(order)


def update_order_status(
    db: Session, order_id: int, new_status: str, current_user: User
) -> OrderResponse:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update order status",
        )

    if new_status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(sorted(VALID_STATUSES))}",
        )

    repo = _get_repo(db)
    order = repo.get_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    order.status = new_status
    repo.save(order)
    return _build_order_response(order)
