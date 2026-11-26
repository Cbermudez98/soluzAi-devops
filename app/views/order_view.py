from fastapi import APIRouter, Path

from app.core.openapi import error_responses
from app.schemas.order import OrderOut, OrderStatusUpdate
from app.views.dependencies import OrderCtrl

router = APIRouter(prefix="/orders", tags=["orders"])

OrderId = Path(description="Identificador interno del pedido (no el código)")


@router.get(
    "/{order_id}",
    response_model=OrderOut,
    summary="Obtener pedido",
    responses=error_responses(404),
)
def get_order(controller: OrderCtrl, order_id: str = OrderId):
    """Devuelve el detalle de un pedido."""
    return controller.get_order(order_id)


@router.patch(
    "/{order_id}/status",
    response_model=OrderOut,
    summary="Actualizar estado del pedido",
    responses=error_responses(404),
)
def update_order_status(data: OrderStatusUpdate, controller: OrderCtrl, order_id: str = OrderId):
    """Cambia el estado del pedido. El agente informa el nuevo estado en el chat."""
    return controller.update_status(order_id, data.status)
