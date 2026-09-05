import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserOut, UserRoleUpdate
from app.api.v1.deps import require_role
from app.models.audit_log import ActorType
from app.services import audit_service

router = APIRouter(prefix="/users", tags=["users"])
ADMIN_ONLY = (UserRole.ADMIN,)

@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_role(*ADMIN_ONLY))):
    return db.scalars(select(User)).all()

@router.patch("/{user_id}/role", response_model=UserOut)
def update_user_role(
    user_id: uuid.UUID, payload: UserRoleUpdate,
    db: Session = Depends(get_db), current_user: User = Depends(require_role(*ADMIN_ONLY)),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    before_role = user.role.value
    user.role = payload.role
    audit_service.log_action(
        db, actor_type=ActorType.HUMAN, actor_id=current_user.id,
        action="user_role_changed", entity_type="user", entity_id=user.id,
        before_state={"role": before_role}, after_state={"role": payload.role.value},
    )
    db.commit(); db.refresh(user)
    return user