def test_complete_customer_purchase_smoke_flow(client, auth_headers):
    admin = auth_headers("admin@example.com", role="admin")

    registered = client.post(
        "/api/auth/register",
        json={"email": "buyer@example.com", "password": "password123"},
    )
    assert registered.status_code == 201

    login = client.post(
        "/api/auth/login",
        json={"email": "buyer@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    buyer = {
        "Authorization": f"Bearer {login.json()['access_token']}"
    }

    flavor = client.post(
        "/api/flavors",
        json={
            "name": "Chocolate",
            "description": "Rich chocolate ice cream",
            "price": "5.00",
            "available": True,
        },
        headers=admin,
    )
    assert flavor.status_code == 201

    catalog = client.get("/api/flavors?page=1&page_size=5")
    assert catalog.status_code == 200
    assert catalog.json()["total"] == 1

    cart_item = client.post(
        "/api/cart/items",
        json={"flavor_id": flavor.json()["id"], "quantity": 2},
        headers=buyer,
    )
    assert cart_item.status_code == 200

    cart_item = client.patch(
        f"/api/cart/items/{cart_item.json()['id']}",
        json={"quantity": 3},
        headers=buyer,
    )
    assert cart_item.status_code == 200
    assert cart_item.json()["quantity"] == 3

    order = client.post("/api/orders", headers=buyer)
    assert order.status_code == 201
    assert order.json()["total_price"] == "15.00"

    assert client.get("/api/cart", headers=buyer).json() == []

    history = client.get("/api/orders", headers=buyer)
    assert history.status_code == 200
    assert history.json()["total"] == 1
    assert history.json()["items"][0]["id"] == order.json()["id"]
