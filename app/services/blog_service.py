from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.blog import Blog
from app.models.user import User
from app.repositories.blog_repository import BlogRepository
from app.schemas.blog import BlogCreate, BlogUpdate


def _get_repo(db: Session) -> BlogRepository:
    return BlogRepository(db)


def _get_blog_or_404(
    repo: BlogRepository, blog_id: int, is_admin: bool
) -> Blog:
    blog = repo.get_by_id(blog_id, is_admin=is_admin)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )
    return blog


def _check_slug_available(
    db: Session, slug: str, exclude_id: Optional[int] = None
) -> None:
    query = db.query(Blog).filter(Blog.slug == slug)
    if exclude_id is not None:
        query = query.filter(Blog.id != exclude_id)
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug already exists",
        )


def create_blog(db: Session, blog_data: BlogCreate, current_user: User) -> Blog:
    repo = _get_repo(db)
    _check_slug_available(db, blog_data.slug)

    blog = Blog(
        title=blog_data.title,
        slug=blog_data.slug,
        content=blog_data.content,
        status="active",
        created_by=current_user.id,
    )
    return repo.create(blog)


def get_blogs(db: Session, current_user: Optional[User]) -> List[Blog]:
    repo = _get_repo(db)
    is_admin = current_user is not None and current_user.is_admin
    return repo.get_all(is_admin=is_admin)


def get_blog(db: Session, blog_id: int, current_user: Optional[User]) -> Blog:
    repo = _get_repo(db)
    is_admin = current_user is not None and current_user.is_admin
    return _get_blog_or_404(repo, blog_id, is_admin=is_admin)


def update_blog(
    db: Session, blog_id: int, blog_data: BlogUpdate, current_user: User
) -> Blog:
    repo = _get_repo(db)

    blog = _get_blog_or_404(repo, blog_id, is_admin=True)

    if blog.created_by != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this blog",
        )

    _check_slug_available(db, blog_data.slug, exclude_id=blog_id)

    blog.title = blog_data.title
    blog.slug = blog_data.slug
    blog.content = blog_data.content
    return repo.save(blog)


def _admin_action(
    db: Session, blog_id: int, current_user: User, target_status: str
) -> Blog:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform this action",
        )

    repo = _get_repo(db)
    blog = _get_blog_or_404(repo, blog_id, is_admin=True)

    opposite = "active" if target_status == "inactive" else "inactive"
    if blog.status != opposite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Blog is already {blog.status}",
        )

    blog.status = target_status
    return repo.save(blog)


def deactivate_blog(db: Session, blog_id: int, current_user: User) -> Blog:
    return _admin_action(db, blog_id, current_user, "inactive")


def activate_blog(db: Session, blog_id: int, current_user: User) -> Blog:
    return _admin_action(db, blog_id, current_user, "active")
