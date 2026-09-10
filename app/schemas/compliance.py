import uuid
from datetime import datetime
from pydantic import BaseModel

class ComplianceResultOut(BaseModel):
    document_id: uuid.UUID
    compliant: bool
    required_approval_level: str
    reasoning: str
    policy_sources: str | None
    model_version: str
    created_at: datetime
    class Config:
        from_attributes = True