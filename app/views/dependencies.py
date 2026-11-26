"""Inyección de controladores en las vistas."""

from typing import Annotated

from fastapi import Depends

from app.controllers.chat_controller import ChatController
from app.controllers.order_controller import OrderController
from app.controllers.store_controller import StoreController


def get_store_controller() -> StoreController:
    return StoreController()


def get_order_controller() -> OrderController:
    return OrderController()


def get_chat_controller() -> ChatController:
    return ChatController()


StoreCtrl = Annotated[StoreController, Depends(get_store_controller)]
OrderCtrl = Annotated[OrderController, Depends(get_order_controller)]
ChatCtrl = Annotated[ChatController, Depends(get_chat_controller)]
