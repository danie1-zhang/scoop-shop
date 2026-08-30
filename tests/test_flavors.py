def flavor_payload(name, *, available=True, price="4.50"):
    return {
        "name": name,
        "description": f"{name} description",
        "price": price,
        "available": available,
    }


def test_only_admin_can_create_update_and_delete_flavors(client, auth_headers):
    admin = auth_headers("admin@example.com", role="admin")
    customer = auth_headers("customer@example.com")

    forbidden = client.post(
        "/api/flavors",
        json=flavor_payload("Vanilla"),
        headers=customer,
    )
    assert forbidden.status_code == 403

    created = client.post(
        "/api/flavors",
        json=flavor_payload("Vanilla"),
        headers=admin,
    )
    assert created.status_code == 201
    flavor_id = created.json()["id"]

    updated = client.patch(
        f"/api/flavors/{flavor_id}",
        json={"price": "5.25"},
        headers=admin,
    )
    assert updated.status_code == 200
    assert updated.json()["price"] == "5.25"

    assert client.patch(
        f"/api/flavors/{flavor_id}",
        json={"price": "6.00"},
        headers=customer,
    ).status_code == 403

    deleted = client.delete(f"/api/flavors/{flavor_id}", headers=admin)
    assert deleted.status_code == 204
    assert client.get(f"/api/flavors/{flavor_id}").status_code == 404


def test_flavor_name_is_case_insensitively_unique(client, auth_headers):
    admin = auth_headers("admin@example.com", role="admin")

    first = client.post(
        "/api/flavors",
        json=flavor_payload("Vanilla"),
        headers=admin,
    )
    duplicate = client.post(
        "/api/flavors",
        json=flavor_payload("vanilla"),
        headers=admin,
    )

    assert first.status_code == 201
    assert duplicate.status_code == 409


def test_flavor_validation(client, auth_headers):
    admin = auth_headers("admin@example.com", role="admin")

    blank_name = client.post(
        "/api/flavors",
        json=flavor_payload("   "),
        headers=admin,
    )
    excessive_precision = client.post(
        "/api/flavors",
        json=flavor_payload("Coffee", price="4.999"),
        headers=admin,
    )

    assert blank_name.status_code == 422
    assert excessive_precision.status_code == 422


def test_flavor_pagination_excludes_unavailable_flavors(
    client, auth_headers
):
    admin = auth_headers("admin@example.com", role="admin")

    for number in range(1, 7):
        response = client.post(
            "/api/flavors",
            json=flavor_payload(f"Flavor {number}"),
            headers=admin,
        )
        assert response.status_code == 201

    client.post(
        "/api/flavors",
        json=flavor_payload("Hidden", available=False),
        headers=admin,
    )

    first_page = client.get("/api/flavors?page=1&page_size=5")
    second_page = client.get("/api/flavors?page=2&page_size=5")

    assert first_page.status_code == 200
    assert first_page.json()["total"] == 6
    assert len(first_page.json()["items"]) == 5
    assert len(second_page.json()["items"]) == 1
    assert all(
        flavor["available"] for flavor in first_page.json()["items"]
    )


def test_flavor_patch_rejects_explicit_null(client, auth_headers):
    admin = auth_headers("admin@example.com", role="admin")
    flavor = client.post(
        "/api/flavors",
        json=flavor_payload("Vanilla"),
        headers=admin,
    ).json()

    response = client.patch(
        f"/api/flavors/{flavor['id']}",
        json={"price": None},
        headers=admin,
    )

    assert response.status_code == 422
