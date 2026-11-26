from app.core.exceptions import ConflictError, NotFoundError
from app.models.entities import Store
from app.models.repositories import StoreRepository
from app.schemas.store import StoreCreate


class StoreController:
    def __init__(self, stores: StoreRepository | None = None) -> None:
        self.stores = stores or StoreRepository()

    def list_stores(self) -> list[Store]:
        return self.stores.list()

    def get_store(self, store_id: str) -> Store:
        store = self.stores.get(store_id)
        if store is None:
            raise NotFoundError(f"Tienda '{store_id}' no encontrada")
        return store

    def create_store(self, data: StoreCreate) -> Store:
        if self.stores.get_by_domain(data.domain):
            raise ConflictError(f"Ya existe una tienda con el dominio '{data.domain}'")
        return self.stores.add(Store(name=data.name, domain=data.domain))
