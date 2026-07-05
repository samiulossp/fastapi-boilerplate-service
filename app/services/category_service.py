from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.user import User
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


def _get_repo(db: Session) -> CategoryRepository:
    return CategoryRepository(db)


def _get_or_404(repo: CategoryRepository, category_id: int, is_admin: bool) -> Category:
    category = repo.get_by_id(category_id, is_admin=is_admin)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    return category


def _check_slug(db: Session, slug: str, exclude_id: Optional[int] = None) -> None:
    query = db.query(Category).filter(Category.slug == slug)
    if exclude_id is not None:
        query = query.filter(Category.id != exclude_id)
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug already exists",
        )


def create_category(db: Session, data: CategoryCreate, current_user: User) -> Category:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create categories",
        )
    repo = _get_repo(db)
    _check_slug(db, data.slug)
    category = Category(name=data.name, slug=data.slug)
    return repo.create(category)


def get_categories(db: Session, current_user: Optional[User]) -> List[Category]:
    repo = _get_repo(db)
    is_admin = current_user is not None and current_user.is_admin
    return repo.get_all(is_admin=is_admin)


def get_category(db: Session, category_id: int, current_user: Optional[User]) -> Category:
    repo = _get_repo(db)
    is_admin = current_user is not None and current_user.is_admin
    return _get_or_404(repo, category_id, is_admin)


def update_category(
    db: Session, category_id: int, data: CategoryUpdate, current_user: User
) -> Category:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update categories",
        )
    repo = _get_repo(db)
    category = _get_or_404(repo, category_id, is_admin=True)
    _check_slug(db, data.slug, exclude_id=category_id)
    category.name = data.name
    category.slug = data.slug
    return repo.save(category)


def _toggle_status(
    db: Session, category_id: int, current_user: User, target: str
) -> Category:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can change category status",
        )
    repo = _get_repo(db)
    category = _get_or_404(repo, category_id, is_admin=True)
    opposite = "active" if target == "inactive" else "inactive"
    if category.status != opposite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category is already {category.status}",
        )
    category.status = target
    return repo.save(category)


def activate_category(db: Session, category_id: int, current_user: User) -> Category:
    return _toggle_status(db, category_id, current_user, "active")


def deactivate_category(db: Session, category_id: int, current_user: User) -> Category:
    return _toggle_status(db, category_id, current_user, "inactive")
