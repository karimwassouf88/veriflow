import uuid
from pydantic import BaseModel
from app.models.purchase_order import PurchaseOrderStatus

class PurchaseOrderCreate(BaseModel):
    po_number: str
    vendor_id: uuid.UUID
    amount: float
    status: PurchaseOrderStatus = PurchaseOrderStatus.OPEN

class PurchaseOrderOut(BaseModel):
    id: uuid.UUID
    po_number: str
    vendor_id: uuid.UUID
    amount: float
    status: PurchaseOrderStatus
    class Config:
        from_attributes = True