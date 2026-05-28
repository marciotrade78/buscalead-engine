from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import parse_csv_setting, settings
from app.middleware.request_id import RequestIdMiddleware


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        version="0.1.0",
    )
    origins = parse_csv_setting(settings.cors_allowed_origins)
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    app.add_middleware(RequestIdMiddleware)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
