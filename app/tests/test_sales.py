from tests.factories import (
    payment_payload,
    receipt_payload,
    sale_item_payload,
    sale_payload,
)


def test_list_sales_when_empty(client, auth_header):
    response = client.get("/sales/", headers=auth_header)
    assert response.status_code == 200
    assert response.json() == []


def test_list_sales(client, auth_header, sale):
    response = client.get("/sales/", headers=auth_header)
    assert response.status_code == 200
    assert [s["sale_id"] for s in response.json()] == [sale["sale_id"]]


def test_create_sale(client, auth_header, customer, admin_user):
    payload = sale_payload(customer["customer_id"], admin_user["user_id"])
    response = client.post("/sales/", json=payload, headers=auth_header)
    assert response.status_code == 201
    body = response.json()
    assert body["sale_id"] > 0
    assert body["customer_id"] == customer["customer_id"]
    assert body["user_id"] == admin_user["user_id"]
    assert float(body["total_amount"]) == 119.98
    assert body["sale_date"]


def test_new_sale_is_unpaid_by_default(client, auth_header, sale):
    assert sale["payment_status"] == "unpaid"


def test_create_sale_with_missing_total_returns_422(client, auth_header, customer, admin_user):
    payload = sale_payload(customer["customer_id"], admin_user["user_id"])
    del payload["total_amount"]
    response = client.post("/sales/", json=payload, headers=auth_header)
    assert response.status_code == 422


def test_create_sale_with_negative_total_returns_422(client, auth_header, customer, admin_user):
    payload = sale_payload(customer["customer_id"], admin_user["user_id"], total_amount="-10")
    response = client.post("/sales/", json=payload, headers=auth_header)
    assert response.status_code == 422


def test_create_sale_with_invalid_payment_status_returns_422(
    client, auth_header, customer, admin_user
):
    payload = sale_payload(
        customer["customer_id"], admin_user["user_id"], payment_status="maybe"
    )
    response = client.post("/sales/", json=payload, headers=auth_header)
    assert response.status_code == 422


def test_create_sale_with_unknown_customer_returns_409(client, auth_header, admin_user):
    payload = sale_payload(9999, admin_user["user_id"])
    response = client.post("/sales/", json=payload, headers=auth_header)
    assert response.status_code == 409


def test_create_sale_with_unknown_user_returns_409(client, auth_header, customer):
    payload = sale_payload(customer["customer_id"], 9999)
    response = client.post("/sales/", json=payload, headers=auth_header)
    assert response.status_code == 409


def test_create_sale_without_login_returns_401(client, customer, admin_user):
    payload = sale_payload(customer["customer_id"], admin_user["user_id"])
    response = client.post("/sales/", json=payload)
    assert response.status_code == 401


def test_cashier_can_create_sales(client, cashier_header, auth_header, customer, admin_user):
    payload = sale_payload(customer["customer_id"], admin_user["user_id"])
    response = client.post("/sales/", json=payload, headers=cashier_header)
    assert response.status_code == 201


def test_get_sale(client, auth_header, sale):
    response = client.get(f"/sales/{sale['sale_id']}", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["sale_id"] == sale["sale_id"]


def test_get_nonexistent_sale_returns_404(client, auth_header):
    response = client.get("/sales/1000", headers=auth_header)
    assert response.status_code == 404
    assert response.json()["detail"] == "Sale not found"


def test_update_sale_payment_status(client, auth_header, sale):
    response = client.put(
        f"/sales/{sale['sale_id']}", json={"payment_status": "paid"}, headers=auth_header
    )
    assert response.status_code == 200
    body = response.json()
    assert body["payment_status"] == "paid"
    assert float(body["total_amount"]) == 119.98


def test_update_sale_with_invalid_payment_status_returns_422(client, auth_header, sale):
    response = client.put(
        f"/sales/{sale['sale_id']}", json={"payment_status": "refunded"}, headers=auth_header
    )
    assert response.status_code == 422


def test_update_nonexistent_sale_returns_404(client, auth_header):
    response = client.put("/sales/1000", json={"payment_status": "paid"}, headers=auth_header)
    assert response.status_code == 404


def test_delete_sale(client, auth_header, sale):
    response = client.delete(f"/sales/{sale['sale_id']}", headers=auth_header)
    assert response.status_code == 204
    response = client.get(f"/sales/{sale['sale_id']}", headers=auth_header)
    assert response.status_code == 404


def test_delete_nonexistent_sale_returns_404(client, auth_header):
    response = client.delete("/sales/1000", headers=auth_header)
    assert response.status_code == 404


def test_deleting_a_sale_also_deletes_its_items(client, auth_header, sale, product):
    client.post(
        "/sale-items/",
        json=sale_item_payload(sale["sale_id"], product["product_id"]),
        headers=auth_header,
    )
    assert len(client.get("/sale-items/", headers=auth_header).json()) == 1

    response = client.delete(f"/sales/{sale['sale_id']}", headers=auth_header)
    assert response.status_code == 204
    assert client.get("/sale-items/", headers=auth_header).json() == []


def test_cannot_delete_a_sale_that_has_a_payment(client, auth_header, sale):
    client.post("/payments/", json=payment_payload(sale["sale_id"]), headers=auth_header)
    response = client.delete(f"/sales/{sale['sale_id']}", headers=auth_header)
    assert response.status_code == 409
    assert client.get(f"/sales/{sale['sale_id']}", headers=auth_header).status_code == 200


def test_cannot_delete_a_sale_that_has_a_receipt(client, auth_header, sale):
    client.post("/receipts/", json=receipt_payload(sale["sale_id"]), headers=auth_header)
    response = client.delete(f"/sales/{sale['sale_id']}", headers=auth_header)
    assert response.status_code == 409
    assert client.get(f"/sales/{sale['sale_id']}", headers=auth_header).status_code == 200
