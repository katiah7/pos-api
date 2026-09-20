from core.security import verify_password
from models.user import User
from tests.factories import user_payload


def test_list_users(client, auth_header, admin_user):
    response = client.get("/users/", headers=auth_header)
    assert response.status_code == 200
    assert [u["username"] for u in response.json()] == ["admin"]


def test_create_user(client, auth_header):
    response = client.post("/users/", json=user_payload(), headers=auth_header)
    assert response.status_code == 201
    body = response.json()
    assert body["user_id"] > 0
    assert body["username"] == "cashier1"
    assert body["full_name"] == "Cashier One"
    assert body["role"] == "cashier"
    assert body["is_active"] is True
    assert body["email"] is None


def test_create_user_with_email(client, auth_header):
    response = client.post(
        "/users/", json=user_payload(email="cashier1@sportshop.co.ke"), headers=auth_header
    )
    assert response.status_code == 201
    assert response.json()["email"] == "cashier1@sportshop.co.ke"


def test_password_is_never_returned(client, auth_header):
    response = client.post("/users/", json=user_payload(), headers=auth_header)
    body = response.json()
    assert "password" not in body
    assert "password_hash" not in body

    listing = client.get("/users/", headers=auth_header).json()
    assert all("password" not in u and "password_hash" not in u for u in listing)


def test_password_is_stored_as_an_argon2_hash(client, auth_header, session_factory):
    created = client.post("/users/", json=user_payload(), headers=auth_header).json()
    with session_factory() as db:
        stored = db.get(User, created["user_id"]).password_hash
    assert stored != "cashier-pass-1"
    assert stored.startswith("$argon2id$")
    assert verify_password("cashier-pass-1", stored)


def test_new_user_can_log_in(client, auth_header):
    client.post("/users/", json=user_payload(), headers=auth_header)
    response = client.post(
        "/auth/login", data={"username": "cashier1", "password": "cashier-pass-1"}
    )
    assert response.status_code == 200


def test_create_user_with_duplicate_username_returns_400(client, auth_header):
    client.post("/users/", json=user_payload(), headers=auth_header)
    response = client.post("/users/", json=user_payload(), headers=auth_header)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already taken"


def test_create_user_with_missing_username_returns_422(client, auth_header):
    payload = user_payload()
    del payload["username"]
    response = client.post("/users/", json=payload, headers=auth_header)
    assert response.status_code == 422


def test_create_user_with_missing_password_returns_422(client, auth_header):
    payload = user_payload()
    del payload["password"]
    response = client.post("/users/", json=payload, headers=auth_header)
    assert response.status_code == 422


def test_create_user_with_short_password_returns_422(client, auth_header):
    response = client.post("/users/", json=user_payload(password="short"), headers=auth_header)
    assert response.status_code == 422


def test_create_user_with_invalid_role_returns_422(client, auth_header):
    response = client.post("/users/", json=user_payload(role="manager"), headers=auth_header)
    assert response.status_code == 422


def test_create_user_with_invalid_email_returns_422(client, auth_header):
    response = client.post("/users/", json=user_payload(email="nope"), headers=auth_header)
    assert response.status_code == 422


def test_create_user_without_login_returns_401(client):
    response = client.post("/users/", json=user_payload())
    assert response.status_code == 401


def test_cashier_cannot_list_users(client, cashier_header):
    response = client.get("/users/", headers=cashier_header)
    assert response.status_code == 403


def test_cashier_cannot_create_users(client, cashier_header):
    response = client.post("/users/", json=user_payload(role="admin"), headers=cashier_header)
    assert response.status_code == 403


def test_get_user(client, auth_header, admin_user):
    response = client.get(f"/users/{admin_user['user_id']}", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["username"] == "admin"


def test_get_nonexistent_user_returns_404(client, auth_header):
    response = client.get("/users/1000", headers=auth_header)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_update_user(client, auth_header):
    created = client.post("/users/", json=user_payload(), headers=auth_header).json()
    response = client.put(
        f"/users/{created['user_id']}",
        json={"full_name": "Cashier Renamed", "role": "admin"},
        headers=auth_header,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] == "Cashier Renamed"
    assert body["role"] == "admin"
    assert body["username"] == "cashier1"


def test_update_password_replaces_the_old_one(client, auth_header):
    created = client.post("/users/", json=user_payload(), headers=auth_header).json()
    response = client.put(
        f"/users/{created['user_id']}", json={"password": "brand-new-pass-1"}, headers=auth_header
    )
    assert response.status_code == 200

    old = client.post("/auth/login", data={"username": "cashier1", "password": "cashier-pass-1"})
    new = client.post("/auth/login", data={"username": "cashier1", "password": "brand-new-pass-1"})
    assert old.status_code == 401
    assert new.status_code == 200


def test_update_without_password_keeps_the_old_password(client, auth_header):
    created = client.post("/users/", json=user_payload(), headers=auth_header).json()
    client.put(f"/users/{created['user_id']}", json={"full_name": "New Name"}, headers=auth_header)
    response = client.post(
        "/auth/login", data={"username": "cashier1", "password": "cashier-pass-1"}
    )
    assert response.status_code == 200


def test_update_user_to_taken_username_returns_409(client, auth_header):
    client.post("/users/", json=user_payload(), headers=auth_header)
    other = client.post(
        "/users/", json=user_payload(username="cashier2"), headers=auth_header
    ).json()
    response = client.put(
        f"/users/{other['user_id']}", json={"username": "cashier1"}, headers=auth_header
    )
    assert response.status_code == 409


def test_update_nonexistent_user_returns_404(client, auth_header):
    response = client.put("/users/1000", json={"full_name": "X"}, headers=auth_header)
    assert response.status_code == 404


def test_delete_user(client, auth_header):
    created = client.post("/users/", json=user_payload(), headers=auth_header).json()
    response = client.delete(f"/users/{created['user_id']}", headers=auth_header)
    assert response.status_code == 204
    response = client.get(f"/users/{created['user_id']}", headers=auth_header)
    assert response.status_code == 404


def test_delete_nonexistent_user_returns_404(client, auth_header):
    response = client.delete("/users/1000", headers=auth_header)
    assert response.status_code == 404


def test_delete_user_who_made_a_sale_returns_409(client, auth_header, sale):
    response = client.delete(f"/users/{sale['user_id']}", headers=auth_header)
    assert response.status_code == 409
