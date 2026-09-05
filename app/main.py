from app.core.logging_config import configure_logging
configure_logging()
from fastapi import FastAPI
from app.api.v1.routes import auth, documents, policy, vendors, approvals,users
from sqlalchemy import text
from app.db.session import SessionLocal
from app.rag.vector_store import get_client as get_qdrant_client


app = FastAPI(title="Veriflow", version="0.1.0")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(policy.router, prefix="/api/v1")
app.include_router(vendors.router, prefix="/api/v1")
app.include_router(approvals.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")

@app.get("/health")
def health():
    report = {"status": "ok", "database": "unknown", "vector_store": "unknown"}
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        report["database"] = "ok"
    except Exception as e:
        report["database"] = f"error: {e}"
        report["status"] = "degraded"
    try:
        get_qdrant_client().get_collections()
        report["vector_store"] = "ok"
    except Exception as e:
        report["vector_store"] = f"error: {e}"
        report["status"] = "degraded"
    return report