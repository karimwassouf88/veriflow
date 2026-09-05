import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.document import Document, IngestionStatus
from app.models.document_extraction import DocumentExtraction
from app.models.vendor import Vendor
from app.models.purchase_order import PurchaseOrder
from app.models.validation_result import ValidationResult
from app.models.audit_log import ActorType
from app.services import audit_service
from app.core.logging_config import log

AMOUNT_TOLERANCE_PCT = 5.0

def run_validation(db: Session, document: Document, actor_id: uuid.UUID) -> ValidationResult:
    document.ingestion_status = IngestionStatus.PROCESSING
    db.commit()
    log.info("validation_started", document_id=str(document.id))
    try:
        rows = db.scalars(select(DocumentExtraction).where(DocumentExtraction.document_id == document.id)).all()
        fields = {row.field_name: row.extracted_value for row in rows}
        vendor_name = fields.get("vendor_name")
        po_reference = fields.get("po_reference")
        total_amount_raw = fields.get("total_amount")

        summary_parts = []
        vendor = None
        vendor_status = "not_found"
        if vendor_name:
            vendor = db.scalar(select(Vendor).where(func.lower(Vendor.name) == vendor_name.strip().lower()))
        if vendor:
            vendor_status = "matched"
            summary_parts.append(f"Vendor '{vendor_name}' matched an existing vendor record.")
        else:
            summary_parts.append(f"Vendor '{vendor_name or 'unknown'}' was not found in vendor records.")

        po = None
        po_status = "not_referenced"
        amount_diff_pct = None
        if po_reference:
            po = db.scalar(select(PurchaseOrder).where(PurchaseOrder.po_number == po_reference.strip()))
            if po is None:
                po_status = "not_found"
                summary_parts.append(f"Referenced PO '{po_reference}' was not found in purchase order records.")
            else:
                try:
                    invoice_amount = float(total_amount_raw) if total_amount_raw is not None else None
                except ValueError:
                    invoice_amount = None
                if invoice_amount is None or not po.amount:
                    po_status = "amount_mismatch"
                    summary_parts.append(f"PO '{po_reference}' found, but the invoice amount could not be compared.")
                else:
                    amount_diff_pct = round(abs(invoice_amount - po.amount) / po.amount * 100, 2)
                    if amount_diff_pct <= AMOUNT_TOLERANCE_PCT:
                        po_status = "matched"
                        summary_parts.append(f"PO '{po_reference}' matched, {amount_diff_pct}% amount difference (within {AMOUNT_TOLERANCE_PCT}% tolerance).")
                    else:
                        po_status = "amount_mismatch"
                        summary_parts.append(f"PO '{po_reference}' found, but amount differs by {amount_diff_pct}%, exceeding the {AMOUNT_TOLERANCE_PCT}% tolerance.")
        else:
            summary_parts.append("No purchase order reference was found on the invoice.")

        passed = vendor_status == "matched" and po_status in ("matched", "not_referenced")

        result = ValidationResult(
            document_id=document.id,
            vendor_id=vendor.id if vendor else None,
            purchase_order_id=po.id if po else None,
            vendor_status=vendor_status,
            po_status=po_status,
            amount_difference_pct=amount_diff_pct,
            summary=" ".join(summary_parts),
            passed=passed,
        )
        db.add(result)
        document.ingestion_status = IngestionStatus.VALIDATED

        audit_service.log_action(
            db, actor_type=ActorType.AGENT, actor_id=actor_id,
            action="document_validated", entity_type="document", entity_id=document.id,
            after_state={"passed": passed, "vendor_status": vendor_status, "po_status": po_status},
        )
        log.info("validation_completed", document_id=str(document.id), passed=passed, vendor_status=vendor_status, po_status=po_status)
        db.commit()
        db.refresh(result)
        return result
    except Exception as e:
        log.error("validation_failed", document_id=str(document.id), error=str(e))
        document.ingestion_status = IngestionStatus.VALIDATION_ERROR
        db.commit()
        raise