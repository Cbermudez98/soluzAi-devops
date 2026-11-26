import time

from app.controllers.store_controller import StoreController
from app.core.exceptions import AppError, NotFoundError
from app.models.entities import Conversation, Message, Role
from app.models.repositories import ConversationRepository, OrderRepository
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent import SupportAgent, agent


class ChatController:
    def __init__(
        self,
        conversations: ConversationRepository | None = None,
        orders: OrderRepository | None = None,
        store_controller: StoreController | None = None,
        support_agent: SupportAgent = agent,
    ) -> None:
        self.conversations = conversations or ConversationRepository()
        self.orders = orders or OrderRepository()
        self.store_controller = store_controller or StoreController()
        self.agent = support_agent

    def chat(self, request: ChatRequest) -> ChatResponse:
        start = time.perf_counter()
        self.store_controller.get_store(request.store_id)
        conversation = self._get_or_create(request)

        reply = self.agent.reply(
            request.message,
            find_order=lambda code: self.orders.get_by_code(request.store_id, code),
        )

        conversation.messages.append(Message(Role.USER, request.message))
        conversation.messages.append(Message(Role.AGENT, reply.text, reply.intent))
        conversation.escalated = conversation.escalated or reply.escalate

        return ChatResponse(
            conversation_id=conversation.id,
            store_id=conversation.store_id,
            reply=reply.text,
            intent=reply.intent,
            escalated=conversation.escalated,
            latency_ms=round((time.perf_counter() - start) * 1000, 3),
        )

    def get_conversation(self, conversation_id: str) -> Conversation:
        conversation = self.conversations.get(conversation_id)
        if conversation is None:
            raise NotFoundError(f"Conversación '{conversation_id}' no encontrada")
        return conversation

    def list_conversations(
        self, store_id: str | None = None, escalated: bool | None = None
    ) -> list[Conversation]:
        return self.conversations.list(store_id=store_id, escalated=escalated)

    def _get_or_create(self, request: ChatRequest) -> Conversation:
        if request.conversation_id is None:
            return self.conversations.add(Conversation(store_id=request.store_id))

        conversation = self.get_conversation(request.conversation_id)
        if conversation.store_id != request.store_id:
            raise AppError("La conversación no pertenece a esta tienda")
        return conversation
