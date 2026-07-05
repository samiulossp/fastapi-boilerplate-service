from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate, UserResponse, UserSignIn
from app.services.auth_service import authenticate_user, create_user, generate_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    user = create_user(db, user_data)
    return user

@router.post("/signin", response_model=TokenResponse)
def signin(credentials: UserSignIn, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials)
    return generate_token(user)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/signout")
def signout():
    return {
        "message": "Logout successful. JWT is stateless — discard the token on the client side."
    }
