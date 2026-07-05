from typing import Optional

from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.cart_item import CartItem


class CartRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> Optional[Cart]:
        return self.db.query(Cart).filter(Cart.user_id == user_id).first()

    def create_cart(self, user_id: int) -> Cart:
        cart = Cart(user_id=user_id)
        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)
        return cart

    def get_or_create_cart(self, user_id: int) -> Cart:
        cart = self.get_by_user_id(user_id)
        if not cart:
            cart = self.create_cart(user_id)
        return cart

    def get_cart_item(self, cart_id: int, product_id: int) -> Optional[CartItem]:
        return (
            self.db.query(CartItem)
            .filter(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
            .first()
        )

    def add_item(self, item: CartItem) -> CartItem:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def save_item(self, item: CartItem) -> CartItem:
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_item(self, item: CartItem) -> None:
        self.db.delete(item)
        self.db.commit()

    def clear_cart(self, cart: Cart) -> None:
        for item in cart.items:
            self.db.delete(item)
        self.db.commit()
