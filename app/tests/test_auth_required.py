"""Every endpoint (except /auth/login) must refuse requests with no login."""
import pytest

PREFIXES = [
    "/products",
    "/categories",
    "/suppliers",
    "/customers",
    "/users",
    "/sales",
    "/sale-items",
    "/payments",
    "/receipts",
]

ENDPOINTS = []
for prefix in PREFIXES:
    ENDPOINTS += [
        ("GET", f"{prefix}/"),
        ("POST", f"{prefix}/"),
        ("GET", f"{prefix}/1"),
        ("PUT", f"{prefix}/1"),
        ("DELETE", f"{prefix}/1"),
    ]


@pytest.mark.parametrize("method,url", ENDPOINTS)
def test_endpoint_without_login_returns_401(client, method, url):
    response = client.request(method, url, json={})
    assert response.status_code == 401


@pytest.mark.parametrize("method,url", ENDPOINTS)
def test_endpoint_with_invalid_token_returns_401(client, method, url):
    response = client.request(
        method, url, json={}, headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


@pytest.mark.parametrize("prefix", [p for p in PREFIXES if p != "/users"])
def test_cashier_can_use_the_shop_endpoints(client, cashier_header, prefix):
    response = client.get(f"{prefix}/", headers=cashier_header)
    assert response.status_code == 200


def test_cashier_is_blocked_from_user_management(client, cashier_header):
    assert client.get("/users/", headers=cashier_header).status_code == 403
