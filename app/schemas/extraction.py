import uuid
from pydantic import BaseModel

class ExtractionFieldOut(BaseModel):
    field_name: str
    extracted_value: str | None
    confidence_score: float
    model_version: str
    class Config:
        from_attributes = True

class DocumentExtractionOut(BaseModel):
    document_id: uuid.UUID
    ingestion_status: str
    fields: list[ExtractionFieldOut]