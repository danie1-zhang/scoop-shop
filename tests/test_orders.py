def add_to_cart(client, headers, flavor_id, quantity=1):
    response = client.post(
        "/api/cart/items",
        json={"flavor_id": flavor_id, "quantity": quantity},
        headers=headers,
    )
    assert response.status_code == 200


def test_checkout_clears_cart_and_returns_history(
    client, auth_headers, create_flavor
):
    customer = auth_headers("customer@example.com")
    flavor = create_flavor(price="4.50")
    add_to_cart(client, customer, flavor.id, quantity=2)

    order = client.post("/api/orders", headers=customer)

    assert order.status_code == 201
    assert order.json()["total_price"] == "9.00"
    assert order.json()["items"][0]["quantity"] == 2
    assert order.json()["items"][0]["flavor_name_at_purchase"] == "Vanilla"
    assert order.json()["items"][0]["price_at_purchase"] == "4.50"
    assert client.get("/api/cart", headers=customer).json() == []

    history = client.get(
        "/api/orders?page=1&page_size=5", headers=customer
    )
    assert history.status_code == 200
    assert history.json()["total"] == 1
    assert len(history.json()["items"]) == 1

    detail = client.get(
        f"/api/orders/{order.json()['id']}", headers=customer
    )
    assert detail.status_code == 200


def test_order_preserves_flavor_name_after_flavor_is_renamed(
    client, auth_headers, create_flavor
):
    customer = auth_headers("customer@example.com")
    admin = auth_headers("admin@example.com", role="admin")
    flavor = create_flavor(name="Vanilla")
    add_to_cart(client, customer, flavor.id)
    order = client.post("/api/orders", headers=customer).json()

    renamed = client.patch(
        f"/api/flavors/{flavor.id}",
        json={"name": "Vanilla Bean"},
        headers=admin,
    )
    assert renamed.status_code == 200

    detail = client.get(
        f"/api/orders/{order['id']}",
        headers=customer,
    )

    assert detail.status_code == 200
    assert detail.json()["items"][0]["flavor_name_at_purchase"] == "Vanilla"


def test_customer_cannot_access_another_customers_order(
    client, auth_headers, create_flavor
):
    owner = auth_headers("owner@example.com")
    other = auth_headers("other@example.com")
    flavor = create_flavor()
    add_to_cart(client, owner, flavor.id)
    order = client.post("/api/orders", headers=owner).json()

    response = client.get(f"/api/orders/{order['id']}", headers=other)

    assert response.status_code == 404


def test_empty_cart_returns_400(client, auth_headers):
    customer = auth_headers("customer@example.com")

    response = client.post("/api/orders", headers=customer)

    assert response.status_code == 400
    assert response.json()["detail"] == "Cart is empty"


def test_checkout_rejects_flavor_that_became_unavailable(
    client, auth_headers, create_flavor
):
    customer = auth_headers("customer@example.com")
    admin = auth_headers("admin@example.com", role="admin")
    flavor = create_flavor()
    add_to_cart(client, customer, flavor.id)
    disabled = client.patch(
        f"/api/flavors/{flavor.id}",
        json={"available": False},
        headers=admin,
    )
    assert disabled.status_code == 200

    response = client.post("/api/orders", headers=customer)

    assert response.status_code == 409
    assert response.json()["detail"] == "Flavor is unavailable"
    assert len(client.get("/api/cart", headers=customer).json()) == 1


def test_sixth_order_attempt_within_minute_returns_429(
    client, auth_headers
):
    customer = auth_headers("customer@example.com")

    statuses = [
        client.post("/api/orders", headers=customer).status_code
        for _ in range(6)
    ]

    assert statuses == [400, 400, 400, 400, 400, 429]
