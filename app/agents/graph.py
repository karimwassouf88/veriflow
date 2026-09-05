import uuid
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from app.db.session import SessionLocal
from app.models.document import Document
from app.services import extraction_service, validation_service, compliance_service, approval_gate_service

class PipelineState(TypedDict):
    document_id: str
    actor_id: str
    extraction_status: str
    validation_status: str
    compliance_status: str
    approval_status: str
    error: Optional[str]

def _extraction_node(state: PipelineState) -> PipelineState:
    db = SessionLocal()
    try:
        document = db.get(Document, uuid.UUID(state["document_id"]))
        extraction_service.run_extraction(db, document, uuid.UUID(state["actor_id"]))
        return {**state, "extraction_status": "completed"}
    except Exception as e:
        return {**state, "extraction_status": "failed", "error": str(e)}
    finally:
        db.close()

def _validation_node(state: PipelineState) -> PipelineState:
    db = SessionLocal()
    try:
        document = db.get(Document, uuid.UUID(state["document_id"]))
        validation_service.run_validation(db, document, uuid.UUID(state["actor_id"]))
        return {**state, "validation_status": "completed"}
    except Exception as e:
        return {**state, "validation_status": "failed", "error": str(e)}
    finally:
        db.close()

def _compliance_node(state: PipelineState) -> PipelineState:
    db = SessionLocal()
    try:
        document = db.get(Document, uuid.UUID(state["document_id"]))
        compliance_service.run_compliance_check(db, document, uuid.UUID(state["actor_id"]))
        return {**state, "compliance_status": "completed"}
    except Exception as e:
        return {**state, "compliance_status": "failed", "error": str(e)}
    finally:
        db.close()

def _route_after_extraction(state: PipelineState) -> str:
    return "validation" if state["extraction_status"] == "completed" else END

def _route_after_validation(state: PipelineState) -> str:
    return "compliance" if state["validation_status"] == "completed" else END

def _build_graph():
    graph = StateGraph(PipelineState)
    graph.add_node("extraction", _extraction_node)
    graph.add_node("validation", _validation_node)
    graph.add_node("compliance", _compliance_node)
    graph.set_entry_point("extraction")
    graph.add_conditional_edges("extraction", _route_after_extraction, {"validation": "validation", END: END})
    graph.add_conditional_edges("validation", _route_after_validation, {"compliance": "compliance", END: END})
    graph.add_edge("compliance", END)
    return graph.compile()

_compiled_graph = None

def run_pipeline(document_id: uuid.UUID, actor_id: uuid.UUID) -> PipelineState:
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = _build_graph()
    initial_state: PipelineState = {
        "document_id": str(document_id), "actor_id": str(actor_id),
        "extraction_status": "pending", "validation_status": "pending",
        "compliance_status": "pending", "error": None,
        "approval_status": "pending"
    }
    return _compiled_graph.invoke(initial_state)

def _approval_gate_node(state: PipelineState) -> PipelineState:
    db = SessionLocal()
    try:
        document = db.get(Document, uuid.UUID(state["document_id"]))
        approval_gate_service.run_approval_gate(db, document, uuid.UUID(state["actor_id"]))
        return {**state, "approval_status": "completed"}
    except Exception as e:
        return {**state, "approval_status": "failed", "error": str(e)}
    finally:
        db.close()

def _route_after_compliance(state: PipelineState) -> str:
    return "approval_gate" if state["compliance_status"] == "completed" else END

def _build_graph():
    graph = StateGraph(PipelineState)
    graph.add_node("extraction", _extraction_node)
    graph.add_node("validation", _validation_node)
    graph.add_node("compliance", _compliance_node)
    graph.add_node("approval_gate", _approval_gate_node)
    graph.set_entry_point("extraction")
    graph.add_conditional_edges("extraction", _route_after_extraction, {"validation": "validation", END: END})
    graph.add_conditional_edges("validation", _route_after_validation, {"compliance": "compliance", END: END})
    graph.add_conditional_edges("compliance", _route_after_compliance, {"approval_gate": "approval_gate", END: END})
    graph.add_edge("approval_gate", END)
    return graph.compile()