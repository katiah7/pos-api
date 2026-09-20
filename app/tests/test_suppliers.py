from tests.factories import supplier_payload


def test_list_suppliers_when_empty(client, auth_header):
    response = client.get("/suppliers/", headers=auth_header)
    assert response.status_code == 200
    assert response.json() == []


def test_list_suppliers(client, auth_header, supplier):
    response = client.get("/suppliers/", headers=auth_header)
    assert response.status_code == 200
    assert [s["supplier_id"] for s in response.json()] == [supplier["supplier_id"]]


def test_create_supplier(client, auth_header):
    response = client.post("/suppliers/", json=supplier_payload(), headers=auth_header)
    assert response.status_code == 201
    body = response.json()
    assert body["supplier_id"] > 0
    assert body["supplier_name"] == "Nike Kenya"
    assert body["contact_person"] == "Amina Otieno"
    assert body["email"] == "orders@nikeke.co.ke"


def test_create_supplier_with_missing_name_returns_422(client, auth_header):
    payload = supplier_payload()
    del payload["supplier_name"]
    response = client.post("/suppliers/", json=payload, headers=auth_header)
    assert response.status_code == 422


def test_create_supplier_with_missing_address_returns_422(client, auth_header):
    payload = supplier_payload()
    del payload["address"]
    response = client.post("/suppliers/", json=payload, headers=auth_header)
    assert response.status_code == 422


def test_create_supplier_with_invalid_email_returns_422(client, auth_header):
    response = client.post(
        "/suppliers/", json=supplier_payload(email="not-an-email"), headers=auth_header
    )
    assert response.status_code == 422


def test_create_supplier_without_login_returns_401(client):
    response = client.post("/suppliers/", json=supplier_payload())
    assert response.status_code == 401


def test_get_supplier(client, auth_header, supplier):
    response = client.get(f"/suppliers/{supplier['supplier_id']}", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["supplier_name"] == "Nike Kenya"


def test_get_nonexistent_supplier_returns_404(client, auth_header):
    response = client.get("/suppliers/1000", headers=auth_header)
    assert response.status_code == 404
    assert response.json()["detail"] == "Supplier not found"


def test_update_supplier(client, auth_header, supplier):
    response = client.put(
        f"/suppliers/{supplier['supplier_id']}",
        json={"contact_person": "Peter Njoroge", "phone": "+254722000003"},
        headers=auth_header,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["contact_person"] == "Peter Njoroge"
    assert body["phone"] == "+254722000003"
    assert body["supplier_name"] == "Nike Kenya"


def test_update_supplier_with_invalid_email_returns_422(client, auth_header, supplier):
    response = client.put(
        f"/suppliers/{supplier['supplier_id']}", json={"email": "nope"}, headers=auth_header
    )
    assert response.status_code == 422


def test_update_nonexistent_supplier_returns_404(client, auth_header):
    response = client.put("/suppliers/1000", json={"phone": "1"}, headers=auth_header)
    assert response.status_code == 404


def test_delete_supplier(client, auth_header, supplier):
    response = client.delete(f"/suppliers/{supplier['supplier_id']}", headers=auth_header)
    assert response.status_code == 204
    response = client.get(f"/suppliers/{supplier['supplier_id']}", headers=auth_header)
    assert response.status_code == 404


def test_delete_nonexistent_supplier_returns_404(client, auth_header):
    response = client.delete("/suppliers/1000", headers=auth_header)
    assert response.status_code == 404


def test_delete_supplier_that_still_has_products_returns_409(client, auth_header, product):
    response = client.delete(f"/suppliers/{product['supplier_id']}", headers=auth_header)
    assert response.status_code == 409
