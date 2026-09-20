from tests.factories import customer_payload


def test_list_customers_when_empty(client, auth_header):
    response = client.get("/customers/", headers=auth_header)
    assert response.status_code == 200
    assert response.json() == []


def test_list_customers(client, auth_header, customer):
    response = client.get("/customers/", headers=auth_header)
    assert response.status_code == 200
    assert [c["customer_id"] for c in response.json()] == [customer["customer_id"]]


def test_create_customer(client, auth_header):
    response = client.post("/customers/", json=customer_payload(), headers=auth_header)
    assert response.status_code == 201
    body = response.json()
    assert body["customer_id"] > 0
    assert body["first_name"] == "Brian"
    assert body["last_name"] == "Mwangi"
    assert body["email"] == "brian@mailbox.co.ke"


def test_new_customer_starts_with_zero_loyalty_points(client, auth_header):
    response = client.post("/customers/", json=customer_payload(), headers=auth_header)
    assert response.json()["loyalty_points"] == 0


def test_create_customer_with_loyalty_points(client, auth_header):
    response = client.post(
        "/customers/", json=customer_payload(loyalty_points=50), headers=auth_header
    )
    assert response.status_code == 201
    assert response.json()["loyalty_points"] == 50


def test_create_customer_with_missing_first_name_returns_422(client, auth_header):
    payload = customer_payload()
    del payload["first_name"]
    response = client.post("/customers/", json=payload, headers=auth_header)
    assert response.status_code == 422


def test_create_customer_with_missing_email_returns_422(client, auth_header):
    payload = customer_payload()
    del payload["email"]
    response = client.post("/customers/", json=payload, headers=auth_header)
    assert response.status_code == 422


def test_create_customer_with_invalid_email_returns_422(client, auth_header):
    response = client.post(
        "/customers/", json=customer_payload(email="brian-at-mail"), headers=auth_header
    )
    assert response.status_code == 422


def test_create_customer_with_negative_loyalty_points_returns_422(client, auth_header):
    response = client.post(
        "/customers/", json=customer_payload(loyalty_points=-1), headers=auth_header
    )
    assert response.status_code == 422


def test_create_customer_without_login_returns_401(client):
    response = client.post("/customers/", json=customer_payload())
    assert response.status_code == 401


def test_get_customer(client, auth_header, customer):
    response = client.get(f"/customers/{customer['customer_id']}", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["first_name"] == "Brian"


def test_get_nonexistent_customer_returns_404(client, auth_header):
    response = client.get("/customers/1000", headers=auth_header)
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"


def test_update_customer(client, auth_header, customer):
    response = client.put(
        f"/customers/{customer['customer_id']}",
        json={"phone": "+254733000004", "loyalty_points": 120},
        headers=auth_header,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["phone"] == "+254733000004"
    assert body["loyalty_points"] == 120
    assert body["first_name"] == "Brian"


def test_update_nonexistent_customer_returns_404(client, auth_header):
    response = client.put("/customers/1000", json={"phone": "1"}, headers=auth_header)
    assert response.status_code == 404


def test_delete_customer(client, auth_header, customer):
    response = client.delete(f"/customers/{customer['customer_id']}", headers=auth_header)
    assert response.status_code == 204
    response = client.get(f"/customers/{customer['customer_id']}", headers=auth_header)
    assert response.status_code == 404


def test_delete_nonexistent_customer_returns_404(client, auth_header):
    response = client.delete("/customers/1000", headers=auth_header)
    assert response.status_code == 404


def test_delete_customer_with_sales_returns_409(client, auth_header, sale):
    response = client.delete(f"/customers/{sale['customer_id']}", headers=auth_header)
    assert response.status_code == 409
