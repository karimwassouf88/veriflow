from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut,UserRole
from app.schemas.auth import Token, RefreshRequest
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.api.v1.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(400, "Email already registered")
    user = User(email=payload.email, hashed_password=hash_password(payload.password), role=UserRole.CLERK)
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == form_data.username))
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    return Token(access_token=create_access_token(str(user.id)), refresh_token=create_refresh_token(str(user.id)))

@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshRequest):
    try:
        decoded = decode_token(payload.refresh_token)
    except ValueError:
        raise HTTPException(401, "Invalid refresh token")
    if decoded.get("type") != "refresh":
        raise HTTPException(401, "Not a refresh token")
    subject = decoded["sub"]
    return Token(access_token=create_access_token(subject), refresh_token=create_refresh_token(subject))

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user