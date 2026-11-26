from fastapi import APIRouter, Path, Query

from app.core.openapi import error_responses
from app.schemas.chat import ChatRequest, ChatResponse, ConversationOut, ConversationSummary
from app.views.dependencies import ChatCtrl

router = APIRouter(tags=["chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Enviar mensaje al agente",
    responses=error_responses(400, 404),
)
def chat(request: ChatRequest, controller: ChatCtrl):
    """
    Envía un mensaje al agente y devuelve su respuesta.

    - Sin `conversation_id` se inicia una conversación nueva.
    - Con `conversation_id` se continúa una existente de la misma tienda.

    Intenciones detectadas: `greeting`, `faq`, `order_status`, `escalation`, `unknown`.
    """
    return controller.chat(request)


@router.get(
    "/conversations",
    response_model=list[ConversationSummary],
    summary="Listar conversaciones",
)
def list_conversations(
    controller: ChatCtrl,
    store_id: str | None = Query(None, description="Filtrar por tienda", examples=["tienda-demo"]),
    escalated: bool | None = Query(None, description="Filtrar por conversaciones escaladas"),
):
    """Devuelve las conversaciones, opcionalmente filtradas."""
    return controller.list_conversations(store_id=store_id, escalated=escalated)


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationOut,
    summary="Historial de una conversación",
    responses=error_responses(404),
)
def get_conversation(
    controller: ChatCtrl,
    conversation_id: str = Path(description="Identificador devuelto por `POST /chat`"),
):
    """Devuelve la conversación con todos sus mensajes."""
    return controller.get_conversation(conversation_id)
