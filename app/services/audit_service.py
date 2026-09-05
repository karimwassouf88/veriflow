import uuid
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog, ActorType

def log_action(
    db: Session,
    *,
    actor_type: ActorType,
    actor_id: uuid.UUID | None,
    action: str,
    entity_type: str,
    entity_id: uuid.UUID,
    before_state: dict | None = None,
    after_state: dict | None = None,
) -> AuditLog:
    entry = AuditLog(
        actor_type=actor_type,
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before_state=before_state,
        after_state=after_state,
    )
    db.add(entry)
    db.flush()
    return entry