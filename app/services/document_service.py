import uuid
import hashlib
import aiofiles
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.document import Document, DocumentType, IngestionStatus
from app.models.audit_log import ActorType
from app.models.user import User
from app.services import audit_service

PDF_MAGIC = b"%PDF-"
CHUNK_SIZE = 1024 * 1024  # 1MB

async def _save_upload_file(file: UploadFile, destination) -> tuple[int, str]:
    first_chunk = await file.read(1024)
    if not first_chunk.startswith(PDF_MAGIC):
        raise ValueError("File is not a valid PDF")

    hasher = hashlib.sha256()
    size = 0
    destination.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(destination, "wb") as out_file:
        hasher.update(first_chunk)
        size += len(first_chunk)
        await out_file.write(first_chunk)
        while chunk := await file.read(CHUNK_SIZE):
            hasher.update(chunk)
            size += len(chunk)
            await out_file.write(chunk)
    return size, hasher.hexdigest()

async def upload_document(db: Session, file: UploadFile, doc_type: DocumentType, user: User) -> Document:
    doc_id = uuid.uuid4()
    destination = settings.documents_storage_path / f"{doc_id}.pdf"

    try:
        size, content_hash = await _save_upload_file(file, destination)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    document = Document(
        id=doc_id,
        type=doc_type,
        uploaded_by=user.id,
        original_filename=file.filename,
        file_path=str(destination),
        file_size=size,
        content_hash=content_hash,
        ingestion_status=IngestionStatus.UPLOADED,
    )
    db.add(document)
    db.flush()

    audit_service.log_action(
        db,
        actor_type=ActorType.HUMAN,
        actor_id=user.id,
        action="document_uploaded",
        entity_type="document",
        entity_id=document.id,
    )
    db.commit()
    db.refresh(document)
    return document