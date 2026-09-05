import uuid
from app.models.document import Document, DocumentType, IngestionStatus
from app.models.document_extraction import DocumentExtraction
from app.models.validation_result import ValidationResult
from app.models.compliance_result import ComplianceResult
from app.models.user import User, UserRole
from app.core.security import hash_password
from app.services.approval_gate_service import run_approval_gate

def _make_document(db_session):
    user = User(email=f"gatetest{uuid.uuid4()}@veriflow.dev", hashed_password=hash_password("x"), role=UserRole.CLERK)
    db_session.add(user); db_session.commit(); db_session.refresh(user)
    doc = Document(type=DocumentType.INVOICE, uploaded_by=user.id, original_filename="x.pdf",
                   file_path="/tmp/x.pdf", file_size=10, content_hash="abc", ingestion_status=IngestionStatus.COMPLIANCE_CHECKED)
    db_session.add(doc); db_session.commit(); db_session.refresh(doc)
    return doc, user

def _add_extraction(db_session, doc_id, field_name, value, confidence):
    db_session.add(DocumentExtraction(document_id=doc_id, field_name=field_name, extracted_value=str(value),
                                       confidence_score=confidence, model_version="test"))
    db_session.commit()

def test_gate_auto_approves_low_amount_clean_case(db_session):
    doc, user = _make_document(db_session)
    _add_extraction(db_session, doc.id, "vendor_name", "Acme Corp", 0.9)
    _add_extraction(db_session, doc.id, "total_amount", "500.00", 0.9)
    db_session.add(ValidationResult(document_id=doc.id, vendor_status="matched", po_status="matched", summary="ok", passed=True))
    db_session.add(ComplianceResult(document_id=doc.id, compliant=True, required_approval_level="none", reasoning="ok", model_version="test"))
    db_session.commit()

    approval = run_approval_gate(db_session, doc, user.id)
    assert approval.decision == "auto_approved"

def test_gate_routes_high_amount_to_human(db_session):
    doc, user = _make_document(db_session)
    _add_extraction(db_session, doc.id, "vendor_name", "Acme Corp", 0.9)
    _add_extraction(db_session, doc.id, "total_amount", "15000.00", 0.9)
    db_session.add(ValidationResult(document_id=doc.id, vendor_status="matched", po_status="matched", summary="ok", passed=True))
    db_session.add(ComplianceResult(document_id=doc.id, compliant=True, required_approval_level="VP", reasoning="ok", model_version="test"))
    db_session.commit()

    approval = run_approval_gate(db_session, doc, user.id)
    assert approval.decision == "pending"

def test_gate_routes_failed_validation_to_human(db_session):
    doc, user = _make_document(db_session)
    _add_extraction(db_session, doc.id, "vendor_name", "Unknown Vendor", 0.9)
    _add_extraction(db_session, doc.id, "total_amount", "500.00", 0.9)
    db_session.add(ValidationResult(document_id=doc.id, vendor_status="not_found", po_status="not_referenced", summary="Vendor not found", passed=False))
    db_session.add(ComplianceResult(document_id=doc.id, compliant=True, required_approval_level="none", reasoning="ok", model_version="test"))
    db_session.commit()

    approval = run_approval_gate(db_session, doc, user.id)
    assert approval.decision == "pending"

def test_gate_routes_low_confidence_to_human(db_session):
    doc, user = _make_document(db_session)
    _add_extraction(db_session, doc.id, "vendor_name", "Acme Corp", 0.3)
    _add_extraction(db_session, doc.id, "total_amount", "500.00", 0.9)
    db_session.add(ValidationResult(document_id=doc.id, vendor_status="matched", po_status="matched", summary="ok", passed=True))
    db_session.add(ComplianceResult(document_id=doc.id, compliant=True, required_approval_level="none", reasoning="ok", model_version="test"))
    db_session.commit()

    approval = run_approval_gate(db_session, doc, user.id)
    assert approval.decision == "pending"