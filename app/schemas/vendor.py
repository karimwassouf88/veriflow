import uuid
from pydantic import BaseModel

class VendorCreate(BaseModel):
    name: str
    tax_id: str | None = None

class VendorOut(BaseModel):
    id: uuid.UUID
    name: str
    tax_id: str | None
    is_active: bool
    class Config:
        from_attributes = True