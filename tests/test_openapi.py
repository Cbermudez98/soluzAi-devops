def test_swagger_ui_available(client):
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text


def test_redoc_available(client):
    assert client.get("/redoc").status_code == 200


def test_openapi_schema(client):
    schema = client.get("/openapi.json").json()
    assert schema["info"]["title"] == "SoporteIA API"
    assert {tag["name"] for tag in schema["tags"]} == {"health", "stores", "orders", "chat"}

    chat = schema["paths"]["/api/v1/chat"]["post"]
    assert chat["summary"] == "Enviar mensaje al agente"
    assert {"200", "400", "404", "422"} <= set(chat["responses"])
    assert "ErrorResponse" in schema["components"]["schemas"]


def test_every_operation_is_documented(client):
    schema = client.get("/openapi.json").json()
    for path, methods in schema["paths"].items():
        for method, operation in methods.items():
            assert operation.get("summary"), f"{method.upper()} {path} sin summary"
            assert operation.get("description"), f"{method.upper()} {path} sin descripción"
