import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.document import DocumentType, IngestionStatus

class DocumentOut(BaseModel):
    id: uuid.UUID
    type: DocumentType
    original_filename: str
    file_size: int
    content_hash: str
    ingestion_status: IngestionStatus
    uploaded_by: uuid.UUID
    created_at: datetime
    class Config:
        from_attributes = True