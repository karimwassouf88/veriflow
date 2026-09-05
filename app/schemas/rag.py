from pydantic import BaseModel

class PolicySearchRequest(BaseModel):
    query: str

class PolicySearchSource(BaseModel):
    document_id: str
    filename: str
    chunk_index: int
    text: str
    rerank_score: float

class PolicySearchResponse(BaseModel):
    query: str
    answer: str
    answerable: bool
    sources: list[PolicySearchSource]