import pytest

from tests.factories import payment_payload, sale_payload


def test_list_payments_when_empty(client, auth_header):
    response = client.get("/payments/", headers=auth_header)
    assert response.status_code == 200
    assert response.json() == []


def test_list_payments(client, auth_header, sale):
    created = client.post(
        "/payments/", json=payment_payload(sale["sale_id"]), headers=auth_header
    ).json()
    response = client.get("/payments/", headers=auth_header)
    assert response.status_code == 200
    assert [p["payment_id"] for p in response.json()] == [created["payment_id"]]


def test_create_payment(client, auth_header, sale):
    response = client.post(
        "/payments/", json=payment_payload(sale["sale_id"]), headers=auth_header
    )
    assert response.status_code == 201
    body = response.json()
    assert body["payment_id"] > 0
    assert body["sale_id"] == sale["sale_id"]
    assert body["payment_method"] == "mpesa"
    assert float(body["amount_paid"]) == 119.98
    assert body["transaction_reference"] == "QGH7X2K9LM"
    assert body["payment_date"]


@pytest.mark.parametrize("method", ["cash", "mpesa", "card", "crypto"])
def test_create_payment_accepts_every_payment_method(client, auth_header, sale, method):
    response = client.post(
        "/payments/",
        json=payment_payload(sale["sale_id"], payment_method=method),
        headers=auth_header,
    )
    assert response.status_code == 201
    assert response.json()["payment_method"] == method


def test_create_payment_with_unknown_method_returns_422(client, auth_header, sale):
    response = client.post(
        "/payments/",
        json=payment_payload(sale["sale_id"], payment_method="paypal"),
        headers=auth_header,
    )
    assert response.status_code == 422


def test_create_payment_with_missing_reference_returns_422(client, auth_header, sale):
    payload = payment_payload(sale["sale_id"])
    del payload["transaction_reference"]
    response = client.post("/payments/", json=payload, headers=auth_header)
    assert response.status_code == 422


def test_create_payment_with_negative_amount_returns_422(client, auth_header, sale):
    response = client.post(
        "/payments/", json=payment_payload(sale["sale_id"], amount_paid="-5"), headers=auth_header
    )
    assert response.status_code == 422


def test_create_payment_for_unknown_sale_returns_409(client, auth_header):
    response = client.post("/payments/", json=payment_payload(9999), headers=auth_header)
    assert response.status_code == 409


def test_a_sale_can_only_have_one_payment(client, auth_header, sale):
    first = client.post("/payments/", json=payment_payload(sale["sale_id"]), headers=auth_header)
    second = client.post(
        "/payments/",
        json=payment_payload(sale["sale_id"], transaction_reference="ANOTHER1"),
        headers=auth_header,
    )
    assert first.status_code == 201
    assert second.status_code == 409


def test_different_sales_can_each_have_a_payment(client, auth_header, sale, customer, admin_user):
    other_sale = client.post(
        "/sales/",
        json=sale_payload(customer["customer_id"], admin_user["user_id"]),
        headers=auth_header,
    ).json()
    first = client.post("/payments/", json=payment_payload(sale["sale_id"]), headers=auth_header)
    second = client.post(
        "/payments/", json=payment_payload(other_sale["sale_id"]), headers=auth_header
    )
    assert first.status_code == 201
    assert second.status_code == 201


def test_create_payment_without_login_returns_401(client, sale):
    response = client.post("/payments/", json=payment_payload(sale["sale_id"]))
    assert response.status_code == 401


def test_get_payment(client, auth_header, sale):
    created = client.post(
        "/payments/", json=payment_payload(sale["sale_id"]), headers=auth_header
    ).json()
    response = client.get(f"/payments/{created['payment_id']}", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["transaction_reference"] == "QGH7X2K9LM"


def test_get_nonexistent_payment_returns_404(client, auth_header):
    response = client.get("/payments/1000", headers=auth_header)
    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"


def test_update_payment(client, auth_header, sale):
    created = client.post(
        "/payments/", json=payment_payload(sale["sale_id"]), headers=auth_header
    ).json()
    response = client.put(
        f"/payments/{created['payment_id']}",
        json={"payment_method": "card", "transaction_reference": "CARD-99"},
        headers=auth_header,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["payment_method"] == "card"
    assert body["transaction_reference"] == "CARD-99"
    assert float(body["amount_paid"]) == 119.98


def test_update_nonexistent_payment_returns_404(client, auth_header):
    response = client.put("/payments/1000", json={"payment_method": "cash"}, headers=auth_header)
    assert response.status_code == 404


def test_delete_payment(client, auth_header, sale):
    created = client.post(
        "/payments/", json=payment_payload(sale["sale_id"]), headers=auth_header
    ).json()
    response = client.delete(f"/payments/{created['payment_id']}", headers=auth_header)
    assert response.status_code == 204
    response = client.get(f"/payments/{created['payment_id']}", headers=auth_header)
    assert response.status_code == 404


def test_delete_nonexistent_payment_returns_404(client, auth_header):
    response = client.delete("/payments/1000", headers=auth_header)
    assert response.status_code == 404
