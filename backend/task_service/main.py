"""
Application entry point for Task Service.
Mirrors project_service/main.py — same factory pattern, task-specific wiring.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.log_config import logger
from app.core.exceptions import TaskServiceError
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.middleware.exception_handler import (
    validation_exception_handler,
    http_exception_handler,
    domain_exception_handler,
    global_exception_handler,
)
from app.db.session import check_db_connection
from app.api.v1.routes import router as v1_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        docs_url="/docs" if settings.APP_DEBUG else None,
        redoc_url=None,
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(TaskServiceError, domain_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)

    app.include_router(v1_router, prefix="/api/v1")

    @app.on_event("startup")
    def on_startup():
        db_ok = check_db_connection()
        logger.info("Task Service started | DB reachable: %s", db_ok)

    @app.get("/health", tags=["Health"])
    def health():
        return {"service": settings.APP_NAME, "status": "ok", "db": check_db_connection()}

    return app


app = create_app()
