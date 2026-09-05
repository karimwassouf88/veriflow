def test_register_and_login(client):
    r = client.post("/api/v1/auth/register", json={"email": "clerk@veriflow.dev", "password": "supersecret123"})
    assert r.status_code == 201
    assert r.json()["role"] == "clerk"

    r = client.post("/api/v1/auth/login", data={"username": "clerk@veriflow.dev", "password": "supersecret123"})
    tokens = r.json()
    assert r.status_code == 200 and "access_token" in tokens

    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert r.status_code == 200 and r.json()["email"] == "clerk@veriflow.dev"



def test_register_ignores_role_field(client):
    r = client.post("/api/v1/auth/register", json={"email": "sneaky@veriflow.dev", "password": "supersecret123", "role": "admin"})
    assert r.status_code == 201
    assert r.json()["role"] == "clerk"

def test_admin_can_promote_user(client):
    from tests.test_documents import _auth_headers
    admin = _auth_headers(client, "roleadmin@veriflow.dev", "admin")
    _auth_headers(client, "target1@veriflow.dev", "clerk")
    users = client.get("/api/v1/users", headers=admin).json()
    target = next(u for u in users if u["email"] == "target1@veriflow.dev")
    r = client.patch(f"/api/v1/users/{target['id']}/role", headers=admin, json={"role": "approver"})
    assert r.status_code == 200
    assert r.json()["role"] == "approver"

def test_non_admin_cannot_list_users(client):
    from tests.test_documents import _auth_headers
    clerk = _auth_headers(client, "clerk40@veriflow.dev", "clerk")
    r = client.get("/api/v1/users", headers=clerk)
    assert r.status_code == 403