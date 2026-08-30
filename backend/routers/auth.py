from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth import create_access_token, hash_password, verify_password
from ..dependencies import get_current_user, get_db
from ..models import User
from ..schemas import LoginRequest, TokenResponse, UserCreate, UserResponse


router = APIRouter(prefix="/api", tags=["authentication"])


@router.post("/auth/register", response_model=UserResponse, status_code=201)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(func.lower(User.email) == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(email=user_data.email, password_hash=hash_password(user_data.password))
    try:
        db.add(user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")
    db.refresh(user)
    return user


@router.post("/auth/login", response_model=TokenResponse)
def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.email) == login_data.email).first()
    if user is None or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
