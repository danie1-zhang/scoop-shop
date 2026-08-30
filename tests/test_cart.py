def test_cart_add_increment_patch_and_delete(
    client, auth_headers, create_flavor
):
    customer = auth_headers("customer@example.com")
    flavor = create_flavor()

    first = client.post(
        "/api/cart/items",
        json={"flavor_id": flavor.id, "quantity": 2},
        headers=customer,
    )
    second = client.post(
        "/api/cart/items",
        json={"flavor_id": flavor.id, "quantity": 3},
        headers=customer,
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["quantity"] == 5
    assert second.json()["flavor"]["name"] == "Vanilla"

    item_id = second.json()["id"]
    patched = client.patch(
        f"/api/cart/items/{item_id}",
        json={"quantity": 7},
        headers=customer,
    )
    assert patched.status_code == 200
    assert patched.json()["quantity"] == 7

    cart = client.get("/api/cart", headers=customer)
    assert cart.status_code == 200
    assert len(cart.json()) == 1

    deleted = client.delete(
        f"/api/cart/items/{item_id}", headers=customer
    )
    assert deleted.status_code == 204
    assert client.get("/api/cart", headers=customer).json() == []


def test_cart_enforces_quantity_limit(client, auth_headers, create_flavor):
    customer = auth_headers("customer@example.com")
    flavor = create_flavor()

    assert client.post(
        "/api/cart/items",
        json={"flavor_id": flavor.id, "quantity": 90},
        headers=customer,
    ).status_code == 200

    overflow = client.post(
        "/api/cart/items",
        json={"flavor_id": flavor.id, "quantity": 11},
        headers=customer,
    )
    invalid_patch = client.patch(
        "/api/cart/items/1",
        json={"quantity": 101},
        headers=customer,
    )

    assert overflow.status_code == 409
    assert invalid_patch.status_code == 422


def test_customer_cannot_modify_another_customers_cart(
    client, auth_headers, create_flavor
):
    owner = auth_headers("owner@example.com")
    other = auth_headers("other@example.com")
    flavor = create_flavor()
    item = client.post(
        "/api/cart/items",
        json={"flavor_id": flavor.id, "quantity": 1},
        headers=owner,
    ).json()

    assert client.patch(
        f"/api/cart/items/{item['id']}",
        json={"quantity": 2},
        headers=other,
    ).status_code == 404
    assert client.delete(
        f"/api/cart/items/{item['id']}", headers=other
    ).status_code == 404


def test_unavailable_flavor_cannot_be_added(
    client, auth_headers, create_flavor
):
    customer = auth_headers("customer@example.com")
    flavor = create_flavor(available=False)

    response = client.post(
        "/api/cart/items",
        json={"flavor_id": flavor.id, "quantity": 1},
        headers=customer,
    )

    assert response.status_code == 409
