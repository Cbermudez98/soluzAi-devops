NEW_ORDER = {"code": "5000", "customer_email": "ana@correo.com", "total": 99000}


def test_list_store_orders(client):
    response = client.get("/api/v1/stores/tienda-demo/orders")
    assert response.status_code == 200
    orders = response.json()
    assert orders
    assert all(order["store_id"] == "tienda-demo" for order in orders)


def test_list_orders_missing_store(client):
    assert client.get("/api/v1/stores/no-existe/orders").status_code == 404


def test_create_get_and_update_order(client):
    created = client.post("/api/v1/stores/tienda-demo/orders", json=NEW_ORDER)
    assert created.status_code == 201
    order = created.json()
    assert order["status"] == "recibido"

    fetched = client.get(f"/api/v1/orders/{order['id']}")
    assert fetched.json()["code"] == "5000"

    updated = client.patch(f"/api/v1/orders/{order['id']}/status", json={"status": "enviado"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "enviado"


def test_create_duplicate_order(client):
    client.post("/api/v1/stores/tienda-demo/orders", json=NEW_ORDER)
    response = client.post("/api/v1/stores/tienda-demo/orders", json=NEW_ORDER)
    assert response.status_code == 409


def test_create_order_invalid_payload(client):
    payload = {"code": "x", "customer_email": "no-es-email", "total": -1}
    assert client.post("/api/v1/stores/tienda-demo/orders", json=payload).status_code == 422


def test_update_order_invalid_status(client):
    order_id = client.get("/api/v1/stores/tienda-demo/orders").json()[0]["id"]
    response = client.patch(f"/api/v1/orders/{order_id}/status", json={"status": "perdido"})
    assert response.status_code == 422


def test_get_missing_order(client):
    assert client.get("/api/v1/orders/no-existe").status_code == 404
