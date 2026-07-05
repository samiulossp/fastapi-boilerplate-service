from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, is_admin: bool = False) -> List[Category]:
        query = self.db.query(Category)
        if not is_admin:
            query = query.filter(Category.status == "active")
        return query.order_by(Category.name).all()

    def get_by_id(self, category_id: int, is_admin: bool = False) -> Optional[Category]:
        query = self.db.query(Category).filter(Category.id == category_id)
        if not is_admin:
            query = query.filter(Category.status == "active")
        return query.first()

    def get_by_slug(self, slug: str) -> Optional[Category]:
        return self.db.query(Category).filter(Category.slug == slug).first()

    def create(self, category: Category) -> Category:
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def save(self, category: Category) -> Category:
        self.db.commit()
        self.db.refresh(category)
        return category
