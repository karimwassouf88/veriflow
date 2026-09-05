import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_error = HTTPException(status.HTTP_401_UNAUTHORIZED, "Could not validate credentials")
    try:
        payload = decode_token(token)
    except ValueError:
        raise credentials_error
    if payload.get("type") != "access":
        raise credentials_error
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_error
    user = db.get(User, uuid.UUID(user_id))
    if user is None or not user.is_active:
        raise credentials_error
    return user

def require_role(*allowed_roles: UserRole):
    def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Not enough permissions")
        return user
    return _check