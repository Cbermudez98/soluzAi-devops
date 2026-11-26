from fastapi import APIRouter, Path, status

from app.core.openapi import error_responses
from app.schemas.order import OrderCreate, OrderOut
from app.schemas.store import StoreCreate, StoreOut
from app.views.dependencies import OrderCtrl, StoreCtrl

router = APIRouter(prefix="/stores", tags=["stores"])

StoreId = Path(description="Identificador de la tienda", examples=["tienda-demo"])


@router.get("", response_model=list[StoreOut], summary="Listar tiendas")
def list_stores(controller: StoreCtrl):
    """Devuelve todas las tiendas registradas."""
    return controller.list_stores()


@router.post(
    "",
    response_model=StoreOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear tienda",
    responses=error_responses(409),
)
def create_store(data: StoreCreate, controller: StoreCtrl):
    """Registra una tienda nueva. El dominio debe ser único."""
    return controller.create_store(data)


@router.get(
    "/{store_id}",
    response_model=StoreOut,
    summary="Obtener tienda",
    responses=error_responses(404),
)
def get_store(controller: StoreCtrl, store_id: str = StoreId):
    """Devuelve el detalle de una tienda."""
    return controller.get_store(store_id)


@router.get(
    "/{store_id}/orders",
    response_model=list[OrderOut],
    summary="Listar pedidos de una tienda",
    responses=error_responses(404),
)
def list_store_orders(controller: OrderCtrl, store_id: str = StoreId):
    """Devuelve los pedidos de la tienda indicada."""
    return controller.list_orders(store_id)


@router.post(
    "/{store_id}/orders",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear pedido",
    responses=error_responses(404, 409),
)
def create_store_order(data: OrderCreate, controller: OrderCtrl, store_id: str = StoreId):
    """Crea un pedido en estado `recibido`. El código debe ser único dentro de la tienda."""
    return controller.create_order(store_id, data)
