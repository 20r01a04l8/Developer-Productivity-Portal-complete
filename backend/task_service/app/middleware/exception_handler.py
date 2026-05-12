import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.log_config import logger
from app.core.exceptions import (
    TaskNotFoundError,
    InvalidTaskOperationError,
    ProjectNotAccessibleError,
    TaskServiceError,
)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
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
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail, "data": None},
    )


async def domain_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    if isinstance(exc, TaskNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": str(exc), "data": None},
        )
    if isinstance(exc, ProjectNotAccessibleError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": str(exc), "data": None},
        )
    if isinstance(exc, InvalidTaskOperationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"success": False, "message": str(exc), "data": None},
        )
    return await global_exception_handler(request, exc)


async def global_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
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
