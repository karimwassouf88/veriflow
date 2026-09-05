from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User, UserRole
from app.api.v1.deps import require_role
from app.schemas.rag import PolicySearchRequest, PolicySearchResponse, PolicySearchSource
from app.rag.retrieval import retrieve_relevant_chunks
from app.agents.policy_qa_agent import answer_from_chunks

router = APIRouter(prefix="/policy-search", tags=["policy"])
ALL_ROLES = (UserRole.ADMIN, UserRole.CLERK, UserRole.APPROVER, UserRole.AUDITOR)

@router.post("", response_model=PolicySearchResponse)
def policy_search(
    payload: PolicySearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*ALL_ROLES)),
):
    chunks = retrieve_relevant_chunks(payload.query, top_k=5)
    result = answer_from_chunks(payload.query, chunks)
    sources = [PolicySearchSource(**{k: c[k] for k in ("document_id", "filename", "chunk_index", "text", "rerank_score")}) for c in chunks]
    return PolicySearchResponse(
        query=payload.query, answer=result.get("answer", ""),
        answerable=result.get("answerable", False), sources=sources,
    )