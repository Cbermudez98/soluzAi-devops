"""Agente simulado de SoporteIA.

Reemplaza a Gemini con reglas simples para que la API sea liviana y
determinista durante las pruebas de carga con k6.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass

from app.models.entities import Intent, Order

FAQ = {
    "horario": "Atendemos de lunes a sábado, de 8:00 a 18:00.",
    "envio": "Los envíos tardan entre 2 y 5 días hábiles.",
    "envío": "Los envíos tardan entre 2 y 5 días hábiles.",
    "devolucion": "Tienes 30 días para devolver un producto sin uso.",
    "devolución": "Tienes 30 días para devolver un producto sin uso.",
    "pago": "Aceptamos tarjeta de crédito, débito y transferencia.",
}

GREETINGS = ("hola", "buenos días", "buenas tardes", "buenas noches")
ESCALATION_WORDS = ("humano", "persona", "asesor", "queja", "reclamo")
ORDER_WORDS = ("pedido", "orden", "compra")
ORDER_CODE = re.compile(r"\b(\d{3,})\b")


@dataclass(frozen=True)
class AgentReply:
    text: str
    intent: Intent
    escalate: bool = False


class SupportAgent:
    def reply(self, message: str, find_order: Callable[[str], Order | None]) -> AgentReply:
        text = message.lower()

        if any(word in text for word in ESCALATION_WORDS):
            return AgentReply(
                "Te comunico con una persona de nuestro equipo.", Intent.ESCALATION, True
            )

        if any(word in text for word in ORDER_WORDS):
            return self._order_reply(text, find_order)

        for key, answer in FAQ.items():
            if key in text:
                return AgentReply(answer, Intent.FAQ)

        if any(text.startswith(greeting) for greeting in GREETINGS):
            return AgentReply("¡Hola! ¿En qué te puedo ayudar hoy?", Intent.GREETING)

        return AgentReply("No entendí tu pregunta. ¿Puedes darme más detalles?", Intent.UNKNOWN)

    @staticmethod
    def _order_reply(text: str, find_order: Callable[[str], Order | None]) -> AgentReply:
        match = ORDER_CODE.search(text)
        if match is None:
            return AgentReply("¿Cuál es el número de tu pedido?", Intent.ORDER_STATUS)

        code = match.group(1)
        order = find_order(code)
        if order is None:
            return AgentReply(
                f"No encontré el pedido {code}. Verifica el número, por favor.",
                Intent.ORDER_STATUS,
            )
        return AgentReply(f"Tu pedido {code} está {order.status}.", Intent.ORDER_STATUS)


agent = SupportAgent()
