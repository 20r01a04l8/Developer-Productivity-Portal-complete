import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.log_config import logger
from app.core.exceptions import (
    ProjectNotFoundError,
    ProjectAlreadyExistsError,
    InvalidProjectOperationError,
    ProjectServiceError,
)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handles Pydantic validation errors (422).
    Formats field-level errors into a readable message.
    FastAPI's default 422 returns a nested array — ours returns a plain string.
    """
    errors = exc.errors()
    messages = [
        f"{' → '.join(str(loc) for loc in e['loc'])}: {e['msg']}"
        for e in errors
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation failed: " + "; ".join(messages),
            "data": None,
        },
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """
    Wraps FastAPI's built-in HTTPException in our APIResponse envelope.
    Without this, FastAPI returns {"detail": "..."} which breaks our uniform shape.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail, "data": None},
    )


async def domain_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Maps typed domain exceptions to HTTP status codes.

    The service layer raises ProjectNotFoundError — it does NOT know about HTTP.
    This handler is the ONLY place that knows "not found = 404".
    """
    if isinstance(exc, ProjectNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": str(exc), "data": None},
        )
    if isinstance(exc, ProjectAlreadyExistsError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"success": False, "message": str(exc), "data": None},
        )
    if isinstance(exc, InvalidProjectOperationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"success": False, "message": str(exc), "data": None},
        )
    return await global_exception_handler(request, exc)


async def global_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Last-resort handler for any unhandled exception.
    Logs the full traceback server-side.
    Returns a safe generic message — NEVER exposes stack traces to the client.
    """
    logger.error(
        "Unhandled exception | %s %s\n%s",
        request.method,
        request.url.path,
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An internal server error occurred.",
            "data": None,
        },
    )
