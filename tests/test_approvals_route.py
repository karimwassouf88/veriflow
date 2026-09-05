from app.models.approval import Approval
from app.models.document import Document, DocumentType, IngestionStatus
from app.models.user import User, UserRole
from app.core.security import hash_password
from tests.test_documents import _auth_headers

def test_approvals_list_and_decide(client, db_session):
    clerk_user = User(email="approvaltest_clerk@veriflow.dev", hashed_password=hash_password("x"), role=UserRole.CLERK)
    db_session.add(clerk_user); db_session.commit(); db_session.refresh(clerk_user)
    doc = Document(type=DocumentType.INVOICE, uploaded_by=clerk_user.id, original_filename="x.pdf",
                   file_path="/tmp/x.pdf", file_size=10, content_hash="abc", ingestion_status=IngestionStatus.COMPLIANCE_CHECKED)
    db_session.add(doc); db_session.commit(); db_session.refresh(doc)
    approval = Approval(document_id=doc.id, decision="pending", routing_reason="test routing")
    db_session.add(approval); db_session.commit(); db_session.refresh(approval)

    approver_headers = _auth_headers(client, "approver1@veriflow.dev", "approver")
    clerk_headers = _auth_headers(client, "clerk30@veriflow.dev", "clerk")

    r = client.post(f"/api/v1/approvals/{approval.id}/decision", headers=clerk_headers, json={"decision": "approved"})
    assert r.status_code == 403

    r = client.get("/api/v1/approvals", headers=approver_headers)
    assert r.status_code == 200
    assert any(a["id"] == str(approval.id) for a in r.json())

    r = client.post(f"/api/v1/approvals/{approval.id}/decision", headers=approver_headers, json={"decision": "approved", "comment": "looks fine"})
    assert r.status_code == 200
    assert r.json()["decision"] == "approved"

    r = client.post(f"/api/v1/approvals/{approval.id}/decision", headers=approver_headers, json={"decision": "rejected"})
    assert r.status_code == 400