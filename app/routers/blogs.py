from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_optional_user
from app.models.user import User
from app.schemas.blog import BlogCreate, BlogResponse, BlogUpdate
from app.services.blog_service import (
    activate_blog,
    create_blog,
    deactivate_blog,
    get_blog,
    get_blogs,
    update_blog,
)

router = APIRouter(prefix="/blogs", tags=["blogs"])

@router.post("", response_model=BlogResponse, status_code=201)
def create(
    body: BlogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_blog(db, body, current_user)

@router.get("", response_model=List[BlogResponse])
def list_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    return get_blogs(db, current_user)

@router.get("/{blog_id}", response_model=BlogResponse)
def detail(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    return get_blog(db, blog_id, current_user)

@router.put("/{blog_id}", response_model=BlogResponse)
def update(
    blog_id: int,
    body: BlogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_blog(db, blog_id, body, current_user)

@router.patch("/{blog_id}/deactivate", response_model=BlogResponse)
def deactivate(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return deactivate_blog(db, blog_id, current_user)

@router.patch("/{blog_id}/activate", response_model=BlogResponse)
def activate(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return activate_blog(db, blog_id, current_user)
