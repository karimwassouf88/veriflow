import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.approval import ApprovalDecision

class ApprovalOut(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    decision: str
    routing_reason: str
    approver_id: uuid.UUID | None
    comment: str | None
    decided_at: datetime | None
    created_at: datetime
    class Config:
        from_attributes = True

class ApprovalDecisionRequest(BaseModel):
    decision: ApprovalDecision
    comment: str | None = None


class ApprovalWithDocumentOut(ApprovalOut):
    document_filename: str | None = None
    document_type: str | None = None