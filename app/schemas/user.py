import uuid
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserRoleUpdate(BaseModel):
    role: UserRole

class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role: UserRole
    is_active: bool
    class Config:
        from_attributes = True
