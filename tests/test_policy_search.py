import io
from tests.test_documents import _auth_headers, MINIMAL_PDF

def test_policy_search(client, monkeypatch):
    import app.api.v1.routes.policy as policy_route
    fake_chunks = [{"document_id": "abc", "filename": "policy.pdf", "chunk_index": 0,
                     "text": "Purchases over $5000 require VP approval.", "rerank_score": 0.9}]
    monkeypatch.setattr(policy_route, "retrieve_relevant_chunks", lambda query, top_k=5: fake_chunks)
    monkeypatch.setattr(policy_route, "answer_from_chunks",
        lambda query, chunks: {"answer": "Purchases over $5000 need VP approval.", "used_excerpts": [0], "answerable": True})

    headers = _auth_headers(client, "clerk8@veriflow.dev", "clerk")
    r = client.post("/api/v1/policy-search", headers=headers, json={"query": "What's the approval threshold?"})
    assert r.status_code == 200
    body = r.json()
    assert body["answerable"] is True
    assert len(body["sources"]) == 1