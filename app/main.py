from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.middleware.request_id import RequestIdMiddleware


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        version="0.1.0",
    )
    app.add_middleware(RequestIdMiddleware)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
