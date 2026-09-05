import io
from tests.test_documents import _auth_headers, MINIMAL_PDF

def _admin_headers(client):
    return _auth_headers(client, "admin1@veriflow.dev", "admin")

def test_validation_all_match(client, monkeypatch):
    import app.services.extraction_service as extraction_service
    monkeypatch.setattr(extraction_service, "extract_text_from_pdf", lambda path: "Invoice text")
    monkeypatch.setattr(extraction_service, "run_extraction_call", lambda raw_text, temperature: {
        "vendor_name": "Acme Corp", "invoice_number": "INV-1", "invoice_date": "2026-01-01",
        "due_date": "2026-02-01", "total_amount": 1000.00, "currency": "USD", "po_reference": "PO-1001",
    })
    admin = _admin_headers(client)
    clerk = _auth_headers(client, "clerk10@veriflow.dev", "clerk")
    vendor = client.post("/api/v1/vendors", headers=admin, json={"name": "Acme Corp"}).json()
    client.post("/api/v1/purchase-orders", headers=admin, json={"po_number": "PO-1001", "vendor_id": vendor["id"], "amount": 1000.00})

    files = {"file": ("invoice.pdf", io.BytesIO(MINIMAL_PDF), "application/pdf")}
    upload = client.post("/api/v1/documents", headers=clerk, data={"doc_type": "invoice"}, files=files)
    doc_id = upload.json()["id"]
    client.post(f"/api/v1/documents/{doc_id}/extract", headers=clerk)

    r = client.post(f"/api/v1/documents/{doc_id}/validate", headers=clerk)
    assert r.status_code == 200
    body = r.json()
    assert body["vendor_status"] == "matched"
    assert body["po_status"] == "matched"
    assert body["passed"] is True

def test_validation_vendor_not_found(client, monkeypatch):
    import app.services.extraction_service as extraction_service
    monkeypatch.setattr(extraction_service, "extract_text_from_pdf", lambda path: "Invoice text")
    monkeypatch.setattr(extraction_service, "run_extraction_call", lambda raw_text, temperature: {
        "vendor_name": "Unknown Vendor LLC", "invoice_number": "INV-2", "invoice_date": "2026-01-01",
        "due_date": "2026-02-01", "total_amount": 500.00, "currency": "USD", "po_reference": None,
    })
    clerk = _auth_headers(client, "clerk11@veriflow.dev", "clerk")
    files = {"file": ("invoice.pdf", io.BytesIO(MINIMAL_PDF), "application/pdf")}
    upload = client.post("/api/v1/documents", headers=clerk, data={"doc_type": "invoice"}, files=files)
    doc_id = upload.json()["id"]
    client.post(f"/api/v1/documents/{doc_id}/extract", headers=clerk)

    r = client.post(f"/api/v1/documents/{doc_id}/validate", headers=clerk)
    body = r.json()
    assert body["vendor_status"] == "not_found"
    assert body["passed"] is False

def test_validation_amount_mismatch(client, monkeypatch):
    import app.services.extraction_service as extraction_service
    monkeypatch.setattr(extraction_service, "extract_text_from_pdf", lambda path: "Invoice text")
    monkeypatch.setattr(extraction_service, "run_extraction_call", lambda raw_text, temperature: {
        "vendor_name": "Beta Supplies", "invoice_number": "INV-3", "invoice_date": "2026-01-01",
        "due_date": "2026-02-01", "total_amount": 1500.00, "currency": "USD", "po_reference": "PO-2002",
    })
    admin = _admin_headers(client)
    clerk = _auth_headers(client, "clerk12@veriflow.dev", "clerk")
    vendor = client.post("/api/v1/vendors", headers=admin, json={"name": "Beta Supplies"}).json()
    client.post("/api/v1/purchase-orders", headers=admin, json={"po_number": "PO-2002", "vendor_id": vendor["id"], "amount": 1000.00})

    files = {"file": ("invoice.pdf", io.BytesIO(MINIMAL_PDF), "application/pdf")}
    upload = client.post("/api/v1/documents", headers=clerk, data={"doc_type": "invoice"}, files=files)
    doc_id = upload.json()["id"]
    client.post(f"/api/v1/documents/{doc_id}/extract", headers=clerk)

    r = client.post(f"/api/v1/documents/{doc_id}/validate", headers=clerk)
    body = r.json()
    assert body["po_status"] == "amount_mismatch"
    assert body["passed"] is False

def test_validate_requires_extraction_first(client):
    clerk = _auth_headers(client, "clerk13@veriflow.dev", "clerk")
    files = {"file": ("invoice.pdf", io.BytesIO(MINIMAL_PDF), "application/pdf")}
    upload = client.post("/api/v1/documents", headers=clerk, data={"doc_type": "invoice"}, files=files)
    doc_id = upload.json()["id"]
    r = client.post(f"/api/v1/documents/{doc_id}/validate", headers=clerk)
    assert r.status_code == 400