import io
from tests.test_documents import _auth_headers, MINIMAL_PDF

def test_process_document_route(client, monkeypatch):
    import app.api.v1.routes.documents as documents_route
    fake_final_state = {
        "extraction_status": "completed", "validation_status": "completed",
        "compliance_status": "completed", "error": None,
    }
    monkeypatch.setattr(documents_route.graph, "run_pipeline", lambda document_id, actor_id: fake_final_state)

    clerk = _auth_headers(client, "clerk21@veriflow.dev", "clerk")
    files = {"file": ("invoice.pdf", io.BytesIO(MINIMAL_PDF), "application/pdf")}
    upload = client.post("/api/v1/documents", headers=clerk, data={"doc_type": "invoice"}, files=files)
    doc_id = upload.json()["id"]

    r = client.post(f"/api/v1/documents/{doc_id}/process", headers=clerk)
    assert r.status_code == 200
    body = r.json()
    assert body["extraction_status"] == "completed"
    assert body["compliance_status"] == "completed"

def test_process_rejects_non_invoice(client):
    clerk = _auth_headers(client, "clerk22@veriflow.dev", "clerk")
    files = {"file": ("policy.pdf", io.BytesIO(MINIMAL_PDF), "application/pdf")}
    upload = client.post("/api/v1/documents", headers=clerk, data={"doc_type": "policy"}, files=files)
    doc_id = upload.json()["id"]
    r = client.post(f"/api/v1/documents/{doc_id}/process", headers=clerk)
    assert r.status_code == 400