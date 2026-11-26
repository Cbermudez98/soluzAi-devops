"""Almacenamiento en memoria.

Suficiente para el laboratorio y las pruebas de carga; se puede reemplazar
por una base de datos real sin tocar controladores ni vistas.
"""

from threading import Lock

from app.models.entities import Conversation, Order, OrderStatus, Store


class InMemoryDatabase:
    def __init__(self) -> None:
        self.lock = Lock()
        self.stores: dict[str, Store] = {}
        self.orders: dict[str, Order] = {}
        self.conversations: dict[str, Conversation] = {}

    def reset(self) -> None:
        with self.lock:
            self.stores.clear()
            self.orders.clear()
            self.conversations.clear()

    def seed(self) -> None:
        demo = Store(id="tienda-demo", name="Tienda Demo", domain="demo.soporteia.co")
        moda = Store(id="tienda-moda", name="Moda Express", domain="moda.soporteia.co")
        self.stores[demo.id] = demo
        self.stores[moda.id] = moda

        statuses = list(OrderStatus)
        for i in range(1, 21):
            store = demo if i % 2 else moda
            order = Order(
                store_id=store.id,
                code=str(1000 + i),
                customer_email=f"cliente{i}@correo.com",
                total=round(25_000 + i * 7_500.5, 2),
                status=statuses[i % len(statuses)],
            )
            self.orders[order.id] = order


db = InMemoryDatabase()
