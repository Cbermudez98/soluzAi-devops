def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root(client):
    body = client.get("/").json()
    assert body["service"] == "soporteia-api"
    assert "version" in body
