import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.log_config import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every HTTP request with method, path, status code, and duration.
    Assigns a unique request_id per request for log correlation.

    The X-Request-ID response header lets clients include the ID in bug reports.
    You can then grep logs for that ID to find the exact request.

    Why middleware instead of logging in each route:
        DRY — one place handles all request logging.
        Routes stay focused on business logic only.
    """

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "[%s] %s %s -> %d (%.1fms)",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        response.headers["X-Request-ID"] = request_id
        return response
