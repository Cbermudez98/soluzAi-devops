from app.controllers.store_controller import StoreController
from app.core.exceptions import ConflictError, NotFoundError
from app.models.entities import Order, OrderStatus
from app.models.repositories import OrderRepository
from app.schemas.order import OrderCreate


class OrderController:
    def __init__(
        self,
        orders: OrderRepository | None = None,
        store_controller: StoreController | None = None,
    ) -> None:
        self.orders = orders or OrderRepository()
        self.store_controller = store_controller or StoreController()

    def list_orders(self, store_id: str) -> list[Order]:
        self.store_controller.get_store(store_id)
        return self.orders.list_by_store(store_id)

    def get_order(self, order_id: str) -> Order:
        order = self.orders.get(order_id)
        if order is None:
            raise NotFoundError(f"Pedido '{order_id}' no encontrado")
        return order

    def create_order(self, store_id: str, data: OrderCreate) -> Order:
        self.store_controller.get_store(store_id)
        if self.orders.get_by_code(store_id, data.code):
            raise ConflictError(f"El pedido '{data.code}' ya existe en la tienda")
        order = Order(
            store_id=store_id,
            code=data.code,
            customer_email=data.customer_email,
            total=data.total,
        )
        return self.orders.add(order)

    def update_status(self, order_id: str, status: OrderStatus) -> Order:
        order = self.get_order(order_id)
        order.status = status
        return order
