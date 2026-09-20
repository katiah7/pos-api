from tests.factories import sale_item_payload


def test_list_sale_items_when_empty(client, auth_header):
    response = client.get("/sale-items/", headers=auth_header)
    assert response.status_code == 200
    assert response.json() == []


def test_list_sale_items(client, auth_header, sale, product):
    created = client.post(
        "/sale-items/",
        json=sale_item_payload(sale["sale_id"], product["product_id"]),
        headers=auth_header,
    ).json()
    response = client.get("/sale-items/", headers=auth_header)
    assert response.status_code == 200
    assert [i["sale_item_id"] for i in response.json()] == [created["sale_item_id"]]


def test_create_sale_item_uses_product_price_and_calculates_subtotal(
    client, auth_header, sale, product
):
    response = client.post(
        "/sale-items/",
        json=sale_item_payload(sale["sale_id"], product["product_id"], quantity=2),
        headers=auth_header,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["sale_item_id"] > 0
    assert body["quantity"] == 2
    assert float(body["unit_price"]) == 59.99  
    assert float(body["subtotal"]) == 119.98  


def test_create_sale_item_with_custom_unit_price(client, auth_header, sale, product):
    response = client.post(
        "/sale-items/",
        json=sale_item_payload(
            sale["sale_id"], product["product_id"], quantity=3, unit_price="50.00"
        ),
        headers=auth_header,
    )
    assert response.status_code == 201
    body = response.json()
    assert float(body["unit_price"]) == 50.00
    assert float(body["subtotal"]) == 150.00


def test_client_cannot_set_the_subtotal(client, auth_header, sale, product):
    payload = sale_item_payload(sale["sale_id"], product["product_id"], subtotal="1.00")
    response = client.post("/sale-items/", json=payload, headers=auth_header)
    assert response.status_code == 201
    assert float(response.json()["subtotal"]) == 119.98


def test_create_sale_item_with_missing_quantity_returns_422(client, auth_header, sale, product):
    payload = sale_item_payload(sale["sale_id"], product["product_id"])
    del payload["quantity"]
    response = client.post("/sale-items/", json=payload, headers=auth_header)
    assert response.status_code == 422


def test_create_sale_item_with_zero_quantity_returns_422(client, auth_header, sale, product):
    payload = sale_item_payload(sale["sale_id"], product["product_id"], quantity=0)
    response = client.post("/sale-items/", json=payload, headers=auth_header)
    assert response.status_code == 422


def test_create_sale_item_with_unknown_product_returns_404(client, auth_header, sale):
    # no unit_price sent, so the service has to look the product up
    response = client.post(
        "/sale-items/", json=sale_item_payload(sale["sale_id"], 9999), headers=auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_create_sale_item_with_unknown_sale_returns_409(client, auth_header, product):
    response = client.post(
        "/sale-items/",
        json=sale_item_payload(9999, product["product_id"]),
        headers=auth_header,
    )
    assert response.status_code == 409


def test_create_sale_item_without_login_returns_401(client, sale, product):
    payload = sale_item_payload(sale["sale_id"], product["product_id"])
    response = client.post("/sale-items/", json=payload)
    assert response.status_code == 401


def test_get_sale_item(client, auth_header, sale, product):
    created = client.post(
        "/sale-items/",
        json=sale_item_payload(sale["sale_id"], product["product_id"]),
        headers=auth_header,
    ).json()
    response = client.get(f"/sale-items/{created['sale_item_id']}", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["product_id"] == product["product_id"]


def test_get_nonexistent_sale_item_returns_404(client, auth_header):
    response = client.get("/sale-items/1000", headers=auth_header)
    assert response.status_code == 404
    assert response.json()["detail"] == "Sale item not found"


def _create_item(client, auth_header, sale, product, **overrides):
    response = client.post(
        "/sale-items/",
        json=sale_item_payload(sale["sale_id"], product["product_id"], **overrides),
        headers=auth_header,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_update_quantity_recalculates_subtotal(client, auth_header, sale, product):
    item = _create_item(client, auth_header, sale, product)
    response = client.put(
        f"/sale-items/{item['sale_item_id']}", json={"quantity": 5}, headers=auth_header
    )
    assert response.status_code == 200
    body = response.json()
    assert body["quantity"] == 5
    assert float(body["unit_price"]) == 59.99
    assert float(body["subtotal"]) == 299.95


def test_update_unit_price_recalculates_subtotal(client, auth_header, sale, product):
    item = _create_item(client, auth_header, sale, product, quantity=2)
    response = client.put(
        f"/sale-items/{item['sale_item_id']}", json={"unit_price": "40.00"}, headers=auth_header
    )
    assert response.status_code == 200
    body = response.json()
    assert body["quantity"] == 2
    assert float(body["subtotal"]) == 80.00


def test_update_unit_price_to_zero_gives_zero_subtotal(client, auth_header, sale, product):
    item = _create_item(client, auth_header, sale, product)
    response = client.put(
        f"/sale-items/{item['sale_item_id']}", json={"unit_price": "0"}, headers=auth_header
    )
    assert response.status_code == 200
    assert float(response.json()["subtotal"]) == 0


def test_update_with_zero_quantity_returns_422(client, auth_header, sale, product):
    item = _create_item(client, auth_header, sale, product)
    response = client.put(
        f"/sale-items/{item['sale_item_id']}", json={"quantity": 0}, headers=auth_header
    )
    assert response.status_code == 422


def test_update_nonexistent_sale_item_returns_404(client, auth_header):
    response = client.put("/sale-items/1000", json={"quantity": 1}, headers=auth_header)
    assert response.status_code == 404


def test_delete_sale_item(client, auth_header, sale, product):
    item = _create_item(client, auth_header, sale, product)
    response = client.delete(f"/sale-items/{item['sale_item_id']}", headers=auth_header)
    assert response.status_code == 204
    response = client.get(f"/sale-items/{item['sale_item_id']}", headers=auth_header)
    assert response.status_code == 404


def test_delete_nonexistent_sale_item_returns_404(client, auth_header):
    response = client.delete("/sale-items/1000", headers=auth_header)
    assert response.status_code == 404


def test_cannot_delete_a_product_that_has_been_sold(client, auth_header, sale, product):
    _create_item(client, auth_header, sale, product)
    response = client.delete(f"/products/{product['product_id']}", headers=auth_header)
    assert response.status_code == 409
