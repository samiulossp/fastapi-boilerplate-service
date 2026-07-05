from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.blog import Blog


class BlogRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, is_admin: bool = False) -> List[Blog]:
        query = self.db.query(Blog)
        if not is_admin:
            query = query.filter(Blog.status == "active")
        return query.order_by(Blog.created_at.desc()).all()

    def get_by_id(self, blog_id: int, is_admin: bool = False) -> Optional[Blog]:
        query = self.db.query(Blog).filter(Blog.id == blog_id)
        if not is_admin:
            query = query.filter(Blog.status == "active")
        return query.first()

    def get_by_slug(self, slug: str) -> Optional[Blog]:
        return self.db.query(Blog).filter(Blog.slug == slug).first()

    def create(self, blog: Blog) -> Blog:
        self.db.add(blog)
        self.db.commit()
        self.db.refresh(blog)
        return blog

    def save(self, blog: Blog) -> Blog:
        self.db.commit()
        self.db.refresh(blog)
        return blog
