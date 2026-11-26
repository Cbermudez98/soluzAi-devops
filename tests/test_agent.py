from app.models.entities import Intent, Order, OrderStatus
from app.services.agent import SupportAgent

agent = SupportAgent()
ORDER = Order(
    store_id="s", code="123", customer_email="a@b.co", total=1, status=OrderStatus.SHIPPED
)


def find(code):
    return ORDER if code == "123" else None


def test_escalation_has_priority():
    reply = agent.reply("tengo una queja con mi pedido 123", find)
    assert reply.intent == Intent.ESCALATION
    assert reply.escalate is True


def test_order_status():
    reply = agent.reply("estado de la orden 123", find)
    assert reply.intent == Intent.ORDER_STATUS
    assert "enviado" in reply.text


def test_faq_with_accent():
    assert agent.reply("info de envío", find).intent == Intent.FAQ
