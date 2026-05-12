import logging
import sys
from app.core.config import settings


def setup_logging() -> logging.Logger:
    """
    Configures the root logger once at import time.
    All modules import `logger` from here — one format, one place to change.

    Why `force=True`:
        Uvicorn configures its own root logger before our app starts.
        Without force=True, basicConfig() is a no-op if the root logger
        already has handlers, meaning our format is silently ignored.
    """
    log_level = logging.DEBUG if settings.APP_DEBUG else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Silence noisy third-party loggers in production
    if not settings.APP_DEBUG:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("passlib").setLevel(logging.WARNING)

    return logging.getLogger(settings.APP_NAME)


logger = setup_logging()
