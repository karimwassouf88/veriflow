from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.vendor import Vendor
from app.models.purchase_order import PurchaseOrder
from app.schemas.vendor import VendorCreate, VendorOut
from app.schemas.purchase_order import PurchaseOrderCreate, PurchaseOrderOut
from app.api.v1.deps import require_role

router = APIRouter(tags=["vendors"])
ADMIN_ONLY = (UserRole.ADMIN,)
ALL_ROLES = (UserRole.ADMIN, UserRole.CLERK, UserRole.APPROVER, UserRole.AUDITOR)

@router.post("/vendors", response_model=VendorOut, status_code=status.HTTP_201_CREATED)
def create_vendor(payload: VendorCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role(*ADMIN_ONLY))):
    vendor = Vendor(name=payload.name, tax_id=payload.tax_id)
    db.add(vendor); db.commit(); db.refresh(vendor)
    return vendor

@router.get("/vendors", response_model=list[VendorOut])
def list_vendors(db: Session = Depends(get_db), current_user: User = Depends(require_role(*ALL_ROLES))):
    return db.scalars(select(Vendor)).all()

@router.post("/purchase-orders", response_model=PurchaseOrderOut, status_code=status.HTTP_201_CREATED)
def create_purchase_order(payload: PurchaseOrderCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role(*ADMIN_ONLY))):
    vendor = db.get(Vendor, payload.vendor_id)
    if vendor is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vendor not found")
    po = PurchaseOrder(po_number=payload.po_number, vendor_id=payload.vendor_id, amount=payload.amount, status=payload.status)
    db.add(po); db.commit(); db.refresh(po)
    return po

@router.get("/purchase-orders", response_model=list[PurchaseOrderOut])
def list_purchase_orders(db: Session = Depends(get_db), current_user: User = Depends(require_role(*ALL_ROLES))):
    return db.scalars(select(PurchaseOrder)).all()