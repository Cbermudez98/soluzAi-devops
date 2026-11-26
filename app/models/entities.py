"""Entidades del dominio."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


def _now() -> datetime:
    return datetime.now(UTC)


def _id() -> str:
    return uuid4().hex


class OrderStatus(StrEnum):
    RECEIVED = "recibido"
    PREPARING = "en preparación"
    SHIPPED = "enviado"
    DELIVERED = "entregado"
    CANCELLED = "cancelado"


class Intent(StrEnum):
    GREETING = "greeting"
    FAQ = "faq"
    ORDER_STATUS = "order_status"
    ESCALATION = "escalation"
    UNKNOWN = "unknown"


class Role(StrEnum):
    USER = "user"
    AGENT = "agent"


@dataclass
class Store:
    name: str
    domain: str
    id: str = field(default_factory=_id)
    created_at: datetime = field(default_factory=_now)


@dataclass
class Order:
    store_id: str
    code: str
    customer_email: str
    total: float
    status: OrderStatus = OrderStatus.RECEIVED
    id: str = field(default_factory=_id)
    created_at: datetime = field(default_factory=_now)


@dataclass
class Message:
    role: Role
    content: str
    intent: Intent | None = None
    created_at: datetime = field(default_factory=_now)


@dataclass
class Conversation:
    store_id: str
    id: str = field(default_factory=_id)
    escalated: bool = False
    messages: list[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=_now)
