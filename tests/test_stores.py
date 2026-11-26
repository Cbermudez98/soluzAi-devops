def test_list_seeded_stores(client):
    response = client.get("/api/v1/stores")
    ids = {store["id"] for store in response.json()}
    assert response.status_code == 200
    assert {"tienda-demo", "tienda-moda"} <= ids


def test_create_and_get_store(client):
    created = client.post("/api/v1/stores", json={"name": "Nueva", "domain": "nueva.com"})
    assert created.status_code == 201
    store_id = created.json()["id"]

    response = client.get(f"/api/v1/stores/{store_id}")
    assert response.status_code == 200
    assert response.json()["domain"] == "nueva.com"


def test_create_store_duplicate_domain(client):
    payload = {"name": "Otra", "domain": "demo.soporteia.co"}
    assert client.post("/api/v1/stores", json=payload).status_code == 409


def test_get_missing_store(client):
    response = client.get("/api/v1/stores/no-existe")
    assert response.status_code == 404
    assert "no encontrada" in response.json()["detail"]
