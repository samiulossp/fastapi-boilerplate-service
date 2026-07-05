from decimal import Decimal
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.user import User
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


def _get_repo(db: Session) -> ProductRepository:
    return ProductRepository(db)


def _get_or_404(repo: ProductRepository, product_id: int, is_admin: bool) -> Product:
    product = repo.get_by_id(product_id, is_admin=is_admin)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


def _check_slug(db: Session, slug: str, exclude_id: Optional[int] = None) -> None:
    query = db.query(Product).filter(Product.slug == slug)
    if exclude_id is not None:
        query = query.filter(Product.id != exclude_id)
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug already exists",
        )


def create_product(db: Session, data: ProductCreate, current_user: User) -> Product:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create products",
        )
    repo = _get_repo(db)
    _check_slug(db, data.slug)
    product = Product(
        category_id=data.category_id,
        name=data.name,
        slug=data.slug,
        description=data.description,
        price=data.price,
        stock=data.stock,
        image=data.image,
    )
    return repo.create(product)


def get_products(
    db: Session,
    current_user: Optional[User],
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[List[Product], int]:
    repo = _get_repo(db)
    is_admin = current_user is not None and current_user.is_admin
    return repo.get_all(
        is_admin=is_admin,
        search=search,
        category_id=category_id,
        page=page,
        per_page=per_page,
    )


def get_product(db: Session, product_id: int, current_user: Optional[User]) -> Product:
    repo = _get_repo(db)
    is_admin = current_user is not None and current_user.is_admin
    return _get_or_404(repo, product_id, is_admin)


def update_product(
    db: Session, product_id: int, data: ProductUpdate, current_user: User
) -> Product:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update products",
        )
    repo = _get_repo(db)
    product = _get_or_404(repo, product_id, is_admin=True)
    _check_slug(db, data.slug, exclude_id=product_id)
    product.category_id = data.category_id
    product.name = data.name
    product.slug = data.slug
    product.description = data.description
    product.price = data.price
    product.stock = data.stock
    product.image = data.image
    return repo.save(product)


def _toggle_status(
    db: Session, product_id: int, current_user: User, target: str
) -> Product:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can change product status",
        )
    repo = _get_repo(db)
    product = _get_or_404(repo, product_id, is_admin=True)
    opposite = "active" if target == "inactive" else "inactive"
    if product.status != opposite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product is already {product.status}",
        )
    product.status = target
    return repo.save(product)


def activate_product(db: Session, product_id: int, current_user: User) -> Product:
    return _toggle_status(db, product_id, current_user, "active")


def deactivate_product(db: Session, product_id: int, current_user: User) -> Product:
    return _toggle_status(db, product_id, current_user, "inactive")
