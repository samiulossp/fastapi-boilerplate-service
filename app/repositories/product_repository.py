from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        is_admin: bool = False,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[List[Product], int]:
        query = self.db.query(Product)
        if not is_admin:
            query = query.filter(Product.status == "active")
        if search:
            query = query.filter(Product.name.ilike(f"%{search}%"))
        if category_id is not None:
            query = query.filter(Product.category_id == category_id)

        total = query.count()
        products = (
            query.order_by(Product.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return products, total

    def get_by_id(self, product_id: int, is_admin: bool = False) -> Optional[Product]:
        query = self.db.query(Product).filter(Product.id == product_id)
        if not is_admin:
            query = query.filter(Product.status == "active")
        return query.first()

    def get_by_slug(self, slug: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.slug == slug).first()

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def save(self, product: Product) -> Product:
        self.db.commit()
        self.db.refresh(product)
        return product
