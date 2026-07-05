from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.user import User
from app.repositories.cart_repository import CartRepository
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse, CartResponse


def _get_repo(db: Session) -> CartRepository:
    return CartRepository(db)


def _get_product_or_404(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


def _check_product_active(product: Product) -> None:
    if product.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is not available",
        )


def _check_stock(product: Product, requested: int) -> None:
    if product.stock < requested:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {product.stock}",
        )


def _build_cart_response(cart: Cart) -> CartResponse:
    items = []
    total = Decimal("0.00")
    for item in cart.items:
        price = item.product.price
        subtotal = price * item.quantity
        total += subtotal
        items.append(
            CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.name,
                product_price=price,
                product_image=item.product.image,
                quantity=item.quantity,
                subtotal=subtotal,
            )
        )
    return CartResponse(id=cart.id, items=items, total=total)


def add_to_cart(db: Session, data: CartItemCreate, current_user: User) -> CartResponse:
    repo = _get_repo(db)
    product = _get_product_or_404(db, data.product_id)
    _check_product_active(product)
    _check_stock(product, data.quantity)

    cart = repo.get_or_create_cart(current_user.id)
    existing = repo.get_cart_item(cart.id, data.product_id)

    if existing:
        new_qty = existing.quantity + data.quantity
        _check_stock(product, new_qty)
        existing.quantity = new_qty
        repo.save_item(existing)
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=data.product_id,
            quantity=data.quantity,
        )
        repo.add_item(item)

    db.refresh(cart)
    return _build_cart_response(cart)


def get_cart(db: Session, current_user: User) -> CartResponse:
    repo = _get_repo(db)
    cart = repo.get_by_user_id(current_user.id)
    if not cart:
        return CartResponse(id=0, items=[], total=Decimal("0.00"))
    return _build_cart_response(cart)


def update_cart_item(
    db: Session, item_id: int, data: CartItemUpdate, current_user: User
) -> CartResponse:
    repo = _get_repo(db)
    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    cart = repo.get_by_user_id(current_user.id)
    if not cart or item.cart_id != cart.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this cart item",
        )

    product = _get_product_or_404(db, item.product_id)
    _check_product_active(product)
    _check_stock(product, data.quantity)

    item.quantity = data.quantity
    repo.save_item(item)
    db.refresh(cart)
    return _build_cart_response(cart)


def remove_cart_item(db: Session, item_id: int, current_user: User) -> CartResponse:
    repo = _get_repo(db)
    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    cart = repo.get_by_user_id(current_user.id)
    if not cart or item.cart_id != cart.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this cart item",
        )

    repo.delete_item(item)
    db.refresh(cart)
    return _build_cart_response(cart)


def clear_cart(db: Session, current_user: User) -> CartResponse:
    repo = _get_repo(db)
    cart = repo.get_by_user_id(current_user.id)
    if not cart:
        return CartResponse(id=0, items=[], total=Decimal("0.00"))
    repo.clear_cart(cart)
    db.refresh(cart)
    return _build_cart_response(cart)
