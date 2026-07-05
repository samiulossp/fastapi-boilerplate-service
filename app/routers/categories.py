from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_optional_user
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.category_service import (
    activate_category,
    create_category,
    deactivate_category,
    get_categories,
    get_category,
    update_category,
)

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("", response_model=CategoryResponse, status_code=201)
def create(
    body: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_category(db, body, current_user)

@router.get("", response_model=List[CategoryResponse])
def list_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    return get_categories(db, current_user)

@router.get("/{category_id}", response_model=CategoryResponse)
def detail(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    return get_category(db, category_id, current_user)

@router.put("/{category_id}", response_model=CategoryResponse)
def update(
    category_id: int,
    body: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_category(db, category_id, body, current_user)

@router.patch("/{category_id}/activate", response_model=CategoryResponse)
def activate(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return activate_category(db, category_id, current_user)

@router.patch("/{category_id}/deactivate", response_model=CategoryResponse)
def deactivate(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return deactivate_category(db, category_id, current_user)
