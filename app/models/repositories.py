"""Acceso a datos de cada entidad."""

from app.models.database import InMemoryDatabase, db
from app.models.entities import Conversation, Order, Store


class StoreRepository:
    def __init__(self, database: InMemoryDatabase = db) -> None:
        self.db = database

    def list(self) -> list[Store]:
        return list(self.db.stores.values())

    def get(self, store_id: str) -> Store | None:
        return self.db.stores.get(store_id)

    def get_by_domain(self, domain: str) -> Store | None:
        return next((s for s in self.db.stores.values() if s.domain == domain), None)

    def add(self, store: Store) -> Store:
        with self.db.lock:
            self.db.stores[store.id] = store
        return store


class OrderRepository:
    def __init__(self, database: InMemoryDatabase = db) -> None:
        self.db = database

    def list_by_store(self, store_id: str) -> list[Order]:
        return [o for o in self.db.orders.values() if o.store_id == store_id]

    def get(self, order_id: str) -> Order | None:
        return self.db.orders.get(order_id)

    def get_by_code(self, store_id: str, code: str) -> Order | None:
        return next(
            (o for o in self.db.orders.values() if o.store_id == store_id and o.code == code),
            None,
        )

    def add(self, order: Order) -> Order:
        with self.db.lock:
            self.db.orders[order.id] = order
        return order


class ConversationRepository:
    def __init__(self, database: InMemoryDatabase = db) -> None:
        self.db = database

    def get(self, conversation_id: str) -> Conversation | None:
        return self.db.conversations.get(conversation_id)

    def list(
        self, store_id: str | None = None, escalated: bool | None = None
    ) -> list[Conversation]:
        items = self.db.conversations.values()
        return [
            c
            for c in items
            if (store_id is None or c.store_id == store_id)
            and (escalated is None or c.escalated == escalated)
        ]

    def add(self, conversation: Conversation) -> Conversation:
        with self.db.lock:
            self.db.conversations[conversation.id] = conversation
        return conversation
