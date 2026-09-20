from tests.factories import category_payload


def test_list_categories_when_empty(client, auth_header):
    response = client.get("/categories/", headers=auth_header)
    assert response.status_code == 200
    assert response.json() == []


def test_list_categories(client, auth_header, category):
    response = client.get("/categories/", headers=auth_header)
    assert response.status_code == 200
    assert [c["category_id"] for c in response.json()] == [category["category_id"]]


def test_create_category(client, auth_header):
    response = client.post("/categories/", json=category_payload(), headers=auth_header)
    assert response.status_code == 201
    body = response.json()
    assert body["category_id"] > 0
    assert body["category_name"] == "Jerseys"
    assert body["description"] == "Team and national jerseys"


def test_create_category_with_missing_name_returns_422(client, auth_header):
    response = client.post(
        "/categories/", json={"description": "No name"}, headers=auth_header
    )
    assert response.status_code == 422


def test_create_category_with_missing_description_returns_422(client, auth_header):
    response = client.post(
        "/categories/", json={"category_name": "Hoodies"}, headers=auth_header
    )
    assert response.status_code == 422


def test_create_category_with_duplicate_name_returns_409(client, auth_header, category):
    response = client.post("/categories/", json=category_payload(), headers=auth_header)
    assert response.status_code == 409


def test_create_category_without_login_returns_401(client):
    response = client.post("/categories/", json=category_payload())
    assert response.status_code == 401


def test_get_category(client, auth_header, category):
    response = client.get(f"/categories/{category['category_id']}", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["category_name"] == "Jerseys"


def test_get_nonexistent_category_returns_404(client, auth_header):
    response = client.get("/categories/1000", headers=auth_header)
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_update_category(client, auth_header, category):
    response = client.put(
        f"/categories/{category['category_id']}",
        json={"category_name": "Hoodies"},
        headers=auth_header,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category_name"] == "Hoodies"
    assert body["description"] == "Team and national jerseys"


def test_update_nonexistent_category_returns_404(client, auth_header):
    response = client.put("/categories/1000", json={"category_name": "X"}, headers=auth_header)
    assert response.status_code == 404


def test_delete_category(client, auth_header, category):
    response = client.delete(f"/categories/{category['category_id']}", headers=auth_header)
    assert response.status_code == 204
    response = client.get(f"/categories/{category['category_id']}", headers=auth_header)
    assert response.status_code == 404


def test_delete_nonexistent_category_returns_404(client, auth_header):
    response = client.delete("/categories/1000", headers=auth_header)
    assert response.status_code == 404


def test_delete_category_that_still_has_products_returns_409(client, auth_header, product):
    response = client.delete(f"/categories/{product['category_id']}", headers=auth_header)
    assert response.status_code == 409
    # and the category is still there
    response = client.get(f"/categories/{product['category_id']}", headers=auth_header)
    assert response.status_code == 200
