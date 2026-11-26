from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.openapi import DESCRIPTION, TAGS_METADATA
from app.models.database import db
from app.views import chat_view, health_view, order_view, store_view


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.seed_data and not db.stores:
        db.seed()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        summary="Agente de atención al cliente para tiendas en línea.",
        description=DESCRIPTION,
        version=settings.app_version,
        openapi_tags=TAGS_METADATA,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        swagger_ui_parameters={"displayRequestDuration": True, "tryItOutEnabled": True},
        lifespan=lifespan,
    )
    register_exception_handlers(app)

    app.include_router(health_view.router)
    for view in (store_view, order_view, chat_view):
        app.include_router(view.router, prefix=settings.api_prefix)

    return app


app = create_app()
