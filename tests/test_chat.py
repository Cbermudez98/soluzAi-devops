def send(client, message, store_id="tienda-demo", conversation_id=None):
    payload = {"store_id": store_id, "message": message, "conversation_id": conversation_id}
    return client.post("/api/v1/chat", json=payload)


def test_chat_faq(client):
    body = send(client, "¿Cuál es el horario?").json()
    assert body["intent"] == "faq"
    assert body["escalated"] is False
    assert body["conversation_id"]


def test_chat_greeting(client):
    assert send(client, "Hola").json()["intent"] == "greeting"


def test_chat_order_found(client, seeded_db):
    order = next(o for o in seeded_db.orders.values() if o.store_id == "tienda-demo")
    body = send(client, f"¿Dónde está mi pedido {order.code}?").json()
    assert body["intent"] == "order_status"
    assert order.status in body["reply"]


def test_chat_order_from_other_store_not_found(client, seeded_db):
    order = next(o for o in seeded_db.orders.values() if o.store_id == "tienda-moda")
    body = send(client, f"pedido {order.code}", store_id="tienda-demo").json()
    assert "No encontré" in body["reply"]


def test_chat_order_without_code(client):
    body = send(client, "quiero saber de mi pedido").json()
    assert body["reply"] == "¿Cuál es el número de tu pedido?"


def test_chat_unknown(client):
    assert send(client, "xyz").json()["intent"] == "unknown"


def test_conversation_history_and_escalation(client):
    first = send(client, "Hola").json()
    conversation_id = first["conversation_id"]

    second = send(client, "quiero hablar con un asesor", conversation_id=conversation_id).json()
    assert second["conversation_id"] == conversation_id
    assert second["escalated"] is True

    history = client.get(f"/api/v1/conversations/{conversation_id}").json()
    assert len(history["messages"]) == 4
    assert history["escalated"] is True

    escalated = client.get("/api/v1/conversations", params={"escalated": True}).json()
    assert [c["id"] for c in escalated] == [conversation_id]


def test_chat_conversation_of_other_store(client):
    conversation_id = send(client, "Hola").json()["conversation_id"]
    response = send(client, "Hola", store_id="tienda-moda", conversation_id=conversation_id)
    assert response.status_code == 400


def test_chat_missing_store(client):
    assert send(client, "Hola", store_id="no-existe").status_code == 404


def test_chat_missing_conversation(client):
    assert send(client, "Hola", conversation_id="no-existe").status_code == 404


def test_chat_validation_error(client):
    assert send(client, "").status_code == 422
