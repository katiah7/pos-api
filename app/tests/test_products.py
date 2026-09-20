from tests.factories import product_payload


def test_list_products_when_empty(client, auth_header):
    response = client.get("/products/", headers=auth_header)
    assert response.status_code == 200
    assert response.json() == []


def test_list_products(client, auth_header, product):
    response = client.get("/products/", headers=auth_header)
    assert response.status_code == 200
    assert [p["product_id"] for p in response.json()] == [product["product_id"]]


def test_create_product(client, auth_header, category, supplier):
    payload = product_payload(category["category_id"], supplier["supplier_id"])
    response = client.post("/products/", json=payload, headers=auth_header)
    assert response.status_code == 201
    body = response.json()
    assert body["product_id"] > 0
    assert body["product_name"] == "Home Jersey"
    assert body["brand"] == "Nike"
    assert float(body["price"]) == 59.99
    assert body["stock_quantity"] == 10
    assert body["barcode"] == "6001234567890"
    assert body["is_active"] is True
    assert body["created_at"]


def test_create_product_with_only_required_fields(client, auth_header, category, supplier):
    payload = {
        "product_name": "Water Bottle",
        "category_id": category["category_id"],
        "supplier_id": supplier["supplier_id"],
        "brand": "Adidas",
        "price": "12.50",
    }
    response = client.post("/products/", json=payload, headers=auth_header)
    assert response.status_code == 201
    body = response.json()
    assert body["size"] is None
    assert body["color"] is None
    assert body["barcode"] is None
    assert body["stock_quantity"] == 0


def test_create_product_with_missing_name_returns_422(client, auth_header, category, supplier):
    payload = product_payload(category["category_id"], supplier["supplier_id"])
    del payload["product_name"]
    response = client.post("/products/", json=payload, headers=auth_header)
    assert response.status_code == 422


def test_create_product_with_negative_price_returns_422(client, auth_header, category, supplier):
    payload = product_payload(category["category_id"], supplier["supplier_id"], price="-1")
    response = client.post("/products/", json=payload, headers=auth_header)
    assert response.status_code == 422


def test_create_product_with_negative_stock_returns_422(client, auth_header, category, supplier):
    payload = product_payload(category["category_id"], supplier["supplier_id"], stock_quantity=-5)
    response = client.post("/products/", json=payload, headers=auth_header)
    assert response.status_code == 422


def test_create_product_with_unknown_category_returns_409(client, auth_header, supplier):
    payload = product_payload(9999, supplier["supplier_id"])
    response = client.post("/products/", json=payload, headers=auth_header)
    assert response.status_code == 409


def test_create_product_with_unknown_supplier_returns_409(client, auth_header, category):
    payload = product_payload(category["category_id"], 9999)
    response = client.post("/products/", json=payload, headers=auth_header)
    assert response.status_code == 409


def test_create_product_with_duplicate_barcode_returns_409(client, auth_header, product):
    payload = product_payload(
        product["category_id"], product["supplier_id"], product_name="Away Jersey"
    )
    response = client.post("/products/", json=payload, headers=auth_header)
    assert response.status_code == 409


def test_create_product_without_login_returns_401(client, category, supplier):
    payload = product_payload(category["category_id"], supplier["supplier_id"])
    response = client.post("/products/", json=payload)
    assert response.status_code == 401


def test_list_products_without_login_returns_401(client):
    response = client.get("/products/")
    assert response.status_code == 401


def test_get_product(client, auth_header, product):
    response = client.get(f"/products/{product['product_id']}", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["product_name"] == "Home Jersey"


def test_get_nonexistent_product_returns_404(client, auth_header):
    response = client.get("/products/1000", headers=auth_header)
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_update_product(client, auth_header, product):
    response = client.put(
        f"/products/{product['product_id']}",
        json={"product_name": "Away Jersey", "price": "64.50", "stock_quantity": 7},
        headers=auth_header,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["product_name"] == "Away Jersey"
    assert float(body["price"]) == 64.50
    assert body["stock_quantity"] == 7
    # fields that were not sent stay the same
    assert body["brand"] == "Nike"
    assert body["barcode"] == "6001234567890"


def test_update_product_can_deactivate_it(client, auth_header, product):
    response = client.put(
        f"/products/{product['product_id']}", json={"is_active": False}, headers=auth_header
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_update_nonexistent_product_returns_404(client, auth_header):
    response = client.put("/products/1000", json={"price": "1.00"}, headers=auth_header)
    assert response.status_code == 404


def test_update_product_with_negative_price_returns_422(client, auth_header, product):
    response = client.put(
        f"/products/{product['product_id']}", json={"price": "-5"}, headers=auth_header
    )
    assert response.status_code == 422


def test_delete_product(client, auth_header, product):
    response = client.delete(f"/products/{product['product_id']}", headers=auth_header)
    assert response.status_code == 204

    response = client.get(f"/products/{product['product_id']}", headers=auth_header)
    assert response.status_code == 404


def test_delete_nonexistent_product_returns_404(client, auth_header):
    response = client.delete("/products/1000", headers=auth_header)
    assert response.status_code == 404
