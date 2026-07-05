from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.order import Order


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, user_id: Optional[int] = None, is_admin: bool = False) -> List[Order]:
        query = self.db.query(Order)
        if not is_admin and user_id is not None:
            query = query.filter(Order.user_id == user_id)
        return query.order_by(Order.created_at.desc()).all()

    def get_by_id(self, order_id: int) -> Optional[Order]:
        return self.db.query(Order).filter(Order.id == order_id).first()

    def create(self, order: Order) -> Order:
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def save(self, order: Order) -> Order:
        self.db.commit()
        self.db.refresh(order)
        return order
