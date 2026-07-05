from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import REFRESH_TOKEN_EXPIRE_DAYS
from app.core.security import create_access_token, hash_password, verify_password
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.user import UserCreate, UserSignIn

def create_user(db: Session, user_data: UserCreate) -> User:
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def authenticate_user(db: Session, credentials: UserSignIn) -> User:
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def _build_token_pair(db: Session, user: User) -> dict:
    access_token = create_access_token(data={"sub": user.email})
    refresh_token_str = RefreshToken.generate_token_str()
    refresh_token = RefreshToken(
        token=refresh_token_str,
        user_id=user.id,
        expires_at=(
            datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        ),
    )
    db.add(refresh_token)
    db.commit()
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
    }

def generate_token(db: Session, user: User) -> dict:
    return _build_token_pair(db, user)

def refresh_user_token(db: Session, refresh_token_str: str) -> dict:
    token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == refresh_token_str)
        .first()
    )
    if not token or not token.is_valid():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    token.revoked = True

    user = db.query(User).filter(User.id == token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return _build_token_pair(db, user)
