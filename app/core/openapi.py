"""Metadatos OpenAPI usados por Swagger UI (/docs) y ReDoc (/redoc)."""

from typing import Any

from pydantic import BaseModel, Field

DESCRIPTION = """
API del agente de atención al cliente de **SoporteIA**.

El agente responde preguntas frecuentes, consulta el estado de los pedidos de cada
tienda y escala la conversación a una persona cuando no puede resolverla.

### Flujo sugerido
1. `GET /api/v1/stores` para elegir una tienda (`tienda-demo` o `tienda-moda`).
2. `POST /api/v1/chat` con un mensaje, por ejemplo *"¿Dónde está mi pedido 1001?"*.
3. Reenviar el `conversation_id` recibido para continuar la conversación.
4. `GET /api/v1/conversations/{id}` para ver el historial.

Los datos viven en memoria y se reinician con cada despliegue.
"""

TAGS_METADATA = [
    {"name": "health", "description": "Estado del servicio. Usado por Cloud Run y el pipeline."},
    {"name": "stores", "description": "Tiendas en línea que usan el agente y sus pedidos."},
    {"name": "orders", "description": "Consulta y actualización de pedidos."},
    {"name": "chat", "description": "Conversaciones con el agente de IA."},
]


class ErrorResponse(BaseModel):
    detail: str = Field(examples=["Tienda 'no-existe' no encontrada"])


def error_responses(*codes: int) -> dict[int | str, dict[str, Any]]:
    """Documenta en OpenAPI los errores de dominio que puede devolver una ruta."""
    descriptions = {
        400: "Solicitud inválida para el estado actual",
        404: "Recurso no encontrado",
        409: "El recurso ya existe",
    }
    return {code: {"model": ErrorResponse, "description": descriptions[code]} for code in codes}
