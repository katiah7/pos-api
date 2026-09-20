from tests.factories import receipt_payload, sale_payload


def test_list_receipts_when_empty(client, auth_header):
    response = client.get("/receipts/", headers=auth_header)
    assert response.status_code == 200
    assert response.json() == []


def test_list_receipts(client, auth_header, sale):
    created = client.post(
        "/receipts/", json=receipt_payload(sale["sale_id"]), headers=auth_header
    ).json()
    response = client.get("/receipts/", headers=auth_header)
    assert response.status_code == 200
    assert [r["receipt_id"] for r in response.json()] == [created["receipt_id"]]


def test_create_receipt(client, auth_header, sale):
    response = client.post(
        "/receipts/", json=receipt_payload(sale["sale_id"]), headers=auth_header
    )
    assert response.status_code == 201
    body = response.json()
    assert body["receipt_id"] > 0
    assert body["sale_id"] == sale["sale_id"]
    assert body["receipt_number"] == "RCPT-0001"
    assert float(body["total_amount"]) == 119.98
    assert body["issue_date"]


def test_create_receipt_with_missing_number_returns_422(client, auth_header, sale):
    payload = receipt_payload(sale["sale_id"])
    del payload["receipt_number"]
    response = client.post("/receipts/", json=payload, headers=auth_header)
    assert response.status_code == 422


def test_create_receipt_with_negative_total_returns_422(client, auth_header, sale):
    response = client.post(
        "/receipts/", json=receipt_payload(sale["sale_id"], total_amount="-1"), headers=auth_header
    )
    assert response.status_code == 422


def test_create_receipt_for_unknown_sale_returns_409(client, auth_header):
    response = client.post("/receipts/", json=receipt_payload(9999), headers=auth_header)
    assert response.status_code == 409


def test_a_sale_can_only_have_one_receipt(client, auth_header, sale):
    first = client.post("/receipts/", json=receipt_payload(sale["sale_id"]), headers=auth_header)
    second = client.post(
        "/receipts/",
        json=receipt_payload(sale["sale_id"], receipt_number="RCPT-0002"),
        headers=auth_header,
    )
    assert first.status_code == 201
    assert second.status_code == 409


def test_receipt_numbers_must_be_unique(client, auth_header, sale, customer, admin_user):
    other_sale = client.post(
        "/sales/",
        json=sale_payload(customer["customer_id"], admin_user["user_id"]),
        headers=auth_header,
    ).json()
    first = client.post("/receipts/", json=receipt_payload(sale["sale_id"]), headers=auth_header)
    second = client.post(
        "/receipts/", json=receipt_payload(other_sale["sale_id"]), headers=auth_header
    )  # same receipt_number, different sale
    assert first.status_code == 201
    assert second.status_code == 409


def test_create_receipt_without_login_returns_401(client, sale):
    response = client.post("/receipts/", json=receipt_payload(sale["sale_id"]))
    assert response.status_code == 401


def test_get_receipt(client, auth_header, sale):
    created = client.post(
        "/receipts/", json=receipt_payload(sale["sale_id"]), headers=auth_header
    ).json()
    response = client.get(f"/receipts/{created['receipt_id']}", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["receipt_number"] == "RCPT-0001"


def test_get_nonexistent_receipt_returns_404(client, auth_header):
    response = client.get("/receipts/1000", headers=auth_header)
    assert response.status_code == 404
    assert response.json()["detail"] == "Receipt not found"


def test_update_receipt(client, auth_header, sale):
    created = client.post(
        "/receipts/", json=receipt_payload(sale["sale_id"]), headers=auth_header
    ).json()
    response = client.put(
        f"/receipts/{created['receipt_id']}",
        json={"receipt_number": "RCPT-0100", "total_amount": "130.00"},
        headers=auth_header,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["receipt_number"] == "RCPT-0100"
    assert float(body["total_amount"]) == 130.00


def test_update_nonexistent_receipt_returns_404(client, auth_header):
    response = client.put("/receipts/1000", json={"receipt_number": "X"}, headers=auth_header)
    assert response.status_code == 404


def test_delete_receipt(client, auth_header, sale):
    created = client.post(
        "/receipts/", json=receipt_payload(sale["sale_id"]), headers=auth_header
    ).json()
    response = client.delete(f"/receipts/{created['receipt_id']}", headers=auth_header)
    assert response.status_code == 204
    response = client.get(f"/receipts/{created['receipt_id']}", headers=auth_header)
    assert response.status_code == 404


def test_delete_nonexistent_receipt_returns_404(client, auth_header):
    response = client.delete("/receipts/1000", headers=auth_header)
    assert response.status_code == 404
