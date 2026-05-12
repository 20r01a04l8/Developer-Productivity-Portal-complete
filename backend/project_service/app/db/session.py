from collections.abc import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# ── Engine ────────────────────────────────────────────────────────────────────
# pool_pre_ping=True: sends "SELECT 1" before reusing a pooled connection.
# Prevents "connection closed" errors after PostgreSQL idle timeouts.
# echo=APP_DEBUG: logs every SQL statement in development, silent in production.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    echo=settings.APP_DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency — yields one Session per HTTP request.

    The finally block guarantees the session is ALWAYS closed,
    even if an exception is raised mid-request. Without this,
    connections leak back into the pool in a broken state.

    Usage in a route:
        @router.get("/projects")
        def list_projects(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """
    Verifies the database is reachable.
    Used by the /health endpoint — returns True if DB responds, False otherwise.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
