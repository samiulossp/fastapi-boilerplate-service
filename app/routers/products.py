from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_optional_user
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product_service import (
    activate_product,
    create_product,
    deactivate_product,
    get_product,
    get_products,
    update_product,
)

router = APIRouter(prefix="/products", tags=["products"])

@router.post("", response_model=ProductResponse, status_code=201)
def create(
    body: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_product(db, body, current_user)

@router.get("", response_model=PaginatedResponse[ProductResponse])
def list_all(
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    products, total = get_products(db, current_user, search, category_id, page, per_page)
    return PaginatedResponse[ProductResponse](
        items=products,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page,
    )

@router.get("/{product_id}", response_model=ProductResponse)
def detail(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    return get_product(db, product_id, current_user)

@router.put("/{product_id}", response_model=ProductResponse)
def update(
    product_id: int,
    body: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_product(db, product_id, body, current_user)

@router.patch("/{product_id}/activate", response_model=ProductResponse)
def activate(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return activate_product(db, product_id, current_user)

@router.patch("/{product_id}/deactivate", response_model=ProductResponse)
def deactivate(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return deactivate_product(db, product_id, current_user)
