from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.entities import Intent, Role


class ChatRequest(BaseModel):
    store_id: str = Field(min_length=1, examples=["tienda-demo"])
    message: str = Field(min_length=1, max_length=1000, examples=["¿Dónde está mi pedido 1001?"])
    conversation_id: str | None = Field(default=None, description="Omitir para iniciar una nueva")


class ChatResponse(BaseModel):
    conversation_id: str
    store_id: str
    reply: str
    intent: Intent
    escalated: bool
    latency_ms: float


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role: Role
    content: str
    intent: Intent | None
    created_at: datetime


class ConversationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    store_id: str
    escalated: bool
    created_at: datetime


class ConversationOut(ConversationSummary):
    messages: list[MessageOut]
