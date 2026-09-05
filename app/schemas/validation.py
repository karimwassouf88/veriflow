import uuid
from pydantic import BaseModel

class ValidationResultOut(BaseModel):
    document_id: uuid.UUID
    vendor_status: str
    po_status: str
    amount_difference_pct: float | None
    summary: str
    passed: bool
    class Config:
        from_attributes = True