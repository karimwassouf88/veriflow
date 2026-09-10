import uuid
from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.document import Document, DocumentType, IngestionStatus
from app.schemas.document import DocumentOut
from app.api.v1.deps import require_role
from app.services import document_service
from app.services import extraction_service
from app.schemas.extraction import DocumentExtractionOut
from app.models.document_extraction import DocumentExtraction
from app.services import rag_ingestion_service
from app.services import validation_service
from app.schemas.validation import ValidationResultOut
from app.agents import graph
from app.models.approval import Approval
from app.models.validation_result import ValidationResult
from app.models.compliance_result import ComplianceResult
from app.schemas.compliance import ComplianceResultOut
from app.schemas.approval import ApprovalOut

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_ROLES = (UserRole.ADMIN, UserRole.CLERK, UserRole.APPROVER)
ALL_ROLES = (UserRole.ADMIN, UserRole.CLERK, UserRole.APPROVER, UserRole.AUDITOR)

@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    doc_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*UPLOAD_ROLES)),
):
    return await document_service.upload_document(db, file, doc_type, current_user)

@router.get("", response_model=list[DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*ALL_ROLES)),
):
    return db.scalars(select(Document).order_by(Document.created_at.desc())).all()

@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*ALL_ROLES)),
):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    return document

@router.get("/{document_id}/download")
def download_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*ALL_ROLES)),
):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    return FileResponse(document.file_path, filename=document.original_filename, media_type="application/pdf")

@router.post("/{document_id}/extract", response_model=DocumentExtractionOut)
def extract_document_route(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*UPLOAD_ROLES)),
):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    if document.type != DocumentType.INVOICE:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Extraction is only supported for invoices right now, got '{document.type.value}'")

    try:
        extraction_service.run_extraction(db, document, current_user.id)
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc))

    fields = db.scalars(select(DocumentExtraction).where(DocumentExtraction.document_id == document.id)).all()
    return DocumentExtractionOut(document_id=document.id, ingestion_status=document.ingestion_status.value, fields=fields)

@router.get("/{document_id}/extraction", response_model=DocumentExtractionOut)
def get_extraction(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*ALL_ROLES)),
):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    fields = db.scalars(select(DocumentExtraction).where(DocumentExtraction.document_id == document.id)).all()
    return DocumentExtractionOut(document_id=document.id, ingestion_status=document.ingestion_status.value, fields=fields)

@router.post("/{document_id}/ingest")
def ingest_document_route(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*UPLOAD_ROLES)),
):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    if document.type != DocumentType.POLICY:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"RAG ingestion is only supported for policy documents right now, got '{document.type.value}'")
    try:
        chunk_count = rag_ingestion_service.ingest_policy_document(db, document, current_user.id)
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc))
    return {"document_id": str(document.id), "ingestion_status": document.ingestion_status.value, "chunk_count": chunk_count}




@router.post("/{document_id}/validate", response_model=ValidationResultOut)
def validate_document_route(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*UPLOAD_ROLES)),
):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    if document.ingestion_status not in (IngestionStatus.EXTRACTED, IngestionStatus.VALIDATED, IngestionStatus.VALIDATION_ERROR):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Document must be extracted before validation, current status: '{document.ingestion_status.value}'")
    return validation_service.run_validation(db, document, current_user.id)


@router.post("/{document_id}/process")
def process_document_route(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*UPLOAD_ROLES)),
):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    if document.type != DocumentType.INVOICE:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The full pipeline currently only supports invoices")

    final_state = graph.run_pipeline(document_id, current_user.id)
    db.refresh(document)
    latest_approval = db.scalars(
        select(Approval).where(Approval.document_id == document.id).order_by(Approval.created_at.desc())
    ).first()

    return {
        "document_id": str(document.id),
        "ingestion_status": document.ingestion_status.value,
        "extraction_status": final_state["extraction_status"],
        "validation_status": final_state["validation_status"],
        "compliance_status": final_state["compliance_status"],
        "approval_status": final_state.get("approval_status"),
        "approval_decision": latest_approval.decision if latest_approval else None,
        "approval_reason": latest_approval.routing_reason if latest_approval else None,
        "error": final_state.get("error"),
    }

def _latest_result(db: Session, model, document_id: uuid.UUID):
    return db.scalars(
        select(model).where(model.document_id == document_id).order_by(model.created_at.desc())
    ).first()

@router.get("/{document_id}/validation", response_model=ValidationResultOut)
def get_validation_result(document_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_role(*ALL_ROLES))):
    if db.get(Document, document_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    result = _latest_result(db, ValidationResult, document_id)
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No validation result yet")
    return result

@router.get("/{document_id}/compliance", response_model=ComplianceResultOut)
def get_compliance_result(document_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_role(*ALL_ROLES))):
    if db.get(Document, document_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    result = _latest_result(db, ComplianceResult, document_id)
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No compliance result yet")
    return result

@router.get("/{document_id}/approval", response_model=ApprovalOut)
def get_approval_result(document_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_role(*ALL_ROLES))):
    if db.get(Document, document_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    result = _latest_result(db, Approval, document_id)
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No approval decision yet")
    return result