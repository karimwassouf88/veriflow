import io

MINIMAL_PDF = b"%PDF-1.4\n%mock pdf content for testing\n%%EOF"

def _auth_headers(client, email, role):
    client.post("/api/v1/auth/register", json={"email": email, "password": "supersecret123"})
    if role != "clerk":
        from tests.conftest import TestingSessionLocal
        from app.models.user import User, UserRole
        db = TestingSessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if user:
                user.role = UserRole(role)
                db.commit()
        finally:
            db.close()
    r = client.post("/api/v1/auth/login", data={"username": email, "password": "supersecret123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}

def test_upload_valid_pdf(client):
    headers = _auth_headers(client, "clerk1@veriflow.dev", "clerk")
    files = {"file": ("invoice.pdf", io.BytesIO(MINIMAL_PDF), "application/pdf")}
    r = client.post("/api/v1/documents", headers=headers, data={"doc_type": "invoice"}, files=files)
    assert r.status_code == 201
    body = r.json()
    assert body["type"] == "invoice"
    assert body["ingestion_status"] == "uploaded"
    assert body["file_size"] == len(MINIMAL_PDF)

def test_upload_rejects_non_pdf(client):
    headers = _auth_headers(client, "clerk2@veriflow.dev", "clerk")
    files = {"file": ("notes.txt", io.BytesIO(b"just some text, not a pdf"), "text/plain")}
    r = client.post("/api/v1/documents", headers=headers, data={"doc_type": "invoice"}, files=files)
    assert r.status_code == 400

def test_auditor_cannot_upload_but_can_list(client):
    headers = _auth_headers(client, "auditor1@veriflow.dev", "auditor")
    files = {"file": ("invoice.pdf", io.BytesIO(MINIMAL_PDF), "application/pdf")}
    r = client.post("/api/v1/documents", headers=headers, data={"doc_type": "invoice"}, files=files)
    assert r.status_code == 403
    r = client.get("/api/v1/documents", headers=headers)
    assert r.status_code == 200

def test_download_document(client):
    headers = _auth_headers(client, "clerk3@veriflow.dev", "clerk")
    files = {"file": ("invoice.pdf", io.BytesIO(MINIMAL_PDF), "application/pdf")}
    upload = client.post("/api/v1/documents", headers=headers, data={"doc_type": "purchase_order"}, files=files)
    doc_id = upload.json()["id"]
    r = client.get(f"/api/v1/documents/{doc_id}/download", headers=headers)
    assert r.status_code == 200
    assert r.content == MINIMAL_PDF


def test_extract_invoice(client, monkeypatch):
    import app.services.extraction_service as extraction_service

    monkeypatch.setattr(
        extraction_service, "extract_text_from_pdf",
        lambda path: "Invoice INV-001\nAcme Corp\nTotal Due: $500.00\nDue: 2026-02-15",
    )

    def fake_run(raw_text, temperature):
        return {
            "vendor_name": "Acme Corp", "invoice_number": "INV-001",
            "invoice_date": "2026-01-15", "due_date": "2026-02-15",
            "total_amount": 500.00, "currency": "USD",
        }
    monkeypatch.setattr(extraction_service, "run_extraction_call", fake_run)

    headers = _auth_headers(client, "clerk4@veriflow.dev", "clerk")
    files = {"file": ("invoice.pdf", io.BytesIO(MINIMAL_PDF), "application/pdf")}
    upload = client.post("/api/v1/documents", headers=headers, data={"doc_type": "invoice"}, files=files)
    doc_id = upload.json()["id"]

    r = client.post(f"/api/v1/documents/{doc_id}/extract", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["ingestion_status"] == "extracted"
    fields = {f["field_name"]: f for f in body["fields"]}
    assert fields["vendor_name"]["extracted_value"] == "Acme Corp"
    assert fields["vendor_name"]["confidence_score"] > 0.5

def test_extract_rejects_non_invoice(client):
    headers = _auth_headers(client, "clerk5@veriflow.dev", "clerk")
    files = {"file": ("policy.pdf", io.BytesIO(MINIMAL_PDF), "application/pdf")}
    upload = client.post("/api/v1/documents", headers=headers, data={"doc_type": "policy"}, files=files)
    doc_id = upload.json()["id"]
    r = client.post(f"/api/v1/documents/{doc_id}/extract", headers=headers)
    assert r.status_code == 400


def test_ingest_policy_document(client, monkeypatch):
    import app.services.rag_ingestion_service as rag_ingestion_service
    monkeypatch.setattr(rag_ingestion_service, "extract_text_from_pdf",
        lambda path: "Section 1\n\nPurchases over $5000 require VP approval.\n\nSection 2\n\nNet 30 terms apply to all vendors.")
    monkeypatch.setattr(rag_ingestion_service.vector_store, "delete_document_chunks", lambda doc_id: None)
    monkeypatch.setattr(rag_ingestion_service.vector_store, "upsert_chunks", lambda doc_id, filename, chunks: len(chunks))

    headers = _auth_headers(client, "clerk6@veriflow.dev", "clerk")
    files = {"file": ("policy.pdf", io.BytesIO(MINIMAL_PDF), "application/pdf")}
    upload = client.post("/api/v1/documents", headers=headers, data={"doc_type": "policy"}, files=files)
    doc_id = upload.json()["id"]

    r = client.post(f"/api/v1/documents/{doc_id}/ingest", headers=headers)
    assert r.status_code == 200
    assert r.json()["ingestion_status"] == "rag_ingested"
    assert r.json()["chunk_count"] >= 1

def test_ingest_rejects_non_policy(client):
    headers = _auth_headers(client, "clerk7@veriflow.dev", "clerk")
    files = {"file": ("invoice.pdf", io.BytesIO(MINIMAL_PDF), "application/pdf")}
    upload = client.post("/api/v1/documents", headers=headers, data={"doc_type": "invoice"}, files=files)
    doc_id = upload.json()["id"]
    r = client.post(f"/api/v1/documents/{doc_id}/ingest", headers=headers)
    assert r.status_code == 400