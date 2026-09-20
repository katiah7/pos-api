from datetime import datetime, timedelta, timezone

import jwt

from core import security
from core.security import create_access_token


def _token_for(sub, key=None, minutes=5):
    payload = {"sub": sub, "exp": datetime.now(timezone.utc) + timedelta(minutes=minutes)}
    return jwt.encode(payload, key or security.SECRET_KEY, algorithm=security.ALGORITHM)


def _bearer(token):
    return {"Authorization": f"Bearer {token}"}


def test_login_returns_a_bearer_token(client, admin_user):
    response = client.post(
        "/auth/login", data={"username": "admin", "password": "admin-pass-123"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_with_wrong_password_returns_401(client, admin_user):
    response = client.post("/auth/login", data={"username": "admin", "password": "wrong-pass"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_login_with_unknown_username_returns_401(client, admin_user):
    response = client.post("/auth/login", data={"username": "ghost", "password": "whatever-1"})
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_with_missing_fields_returns_422(client):
    response = client.post("/auth/login", data={"username": "admin"})
    assert response.status_code == 422


def test_login_of_inactive_user_returns_403(client, auth_header, admin_user):
    created = client.post(
        "/users/",
        json={"username": "temp", "password": "temp-pass-123", "full_name": "T", "role": "cashier"},
        headers=auth_header,
    ).json()
    client.put(f"/users/{created['user_id']}", json={"is_active": False}, headers=auth_header)
    response = client.post("/auth/login", data={"username": "temp", "password": "temp-pass-123"})
    assert response.status_code == 403


def test_me_returns_the_logged_in_user(client, auth_header):
    response = client.get("/auth/me", headers=auth_header)
    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "admin"
    assert body["role"] == "admin"
    assert "password_hash" not in body


def test_me_without_token_returns_401(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_with_garbage_token_returns_401(client):
    response = client.get("/auth/me", headers=_bearer("not-a-jwt"))
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_with_expired_token_returns_401(client, admin_user):
    token = _token_for(str(admin_user["user_id"]), minutes=-1)
    response = client.get("/auth/me", headers=_bearer(token))
    assert response.status_code == 401


def test_me_with_token_signed_by_someone_else_returns_401(client, admin_user):
    token = _token_for(str(admin_user["user_id"]), key="x" * 40)
    response = client.get("/auth/me", headers=_bearer(token))
    assert response.status_code == 401


def test_me_with_non_numeric_subject_returns_401(client, admin_user):
    response = client.get("/auth/me", headers=_bearer(_token_for("abc")))
    assert response.status_code == 401


def test_me_with_zero_subject_returns_401(client, admin_user):
    response = client.get("/auth/me", headers=_bearer(_token_for("0")))
    assert response.status_code == 401


def test_me_with_token_without_subject_returns_401(client, admin_user):
    payload = {"exp": datetime.now(timezone.utc) + timedelta(minutes=5)}
    token = jwt.encode(payload, security.SECRET_KEY, algorithm=security.ALGORITHM)
    response = client.get("/auth/me", headers=_bearer(token))
    assert response.status_code == 401


def test_me_for_deleted_user_returns_401(client, admin_user):
    response = client.get("/auth/me", headers=_bearer(create_access_token(9999)))
    assert response.status_code == 401


def test_deactivated_user_is_rejected_even_with_a_valid_token(client, auth_header, admin_user):
    client.put(
        f"/users/{admin_user['user_id']}", json={"is_active": False}, headers=auth_header
    )
    response = client.get("/auth/me", headers=auth_header)
    assert response.status_code == 403
