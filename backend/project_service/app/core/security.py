from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

bearer_scheme = HTTPBearer()


class TokenPayload(BaseModel):
    """
    Typed JWT payload — prevents raw dict access and KeyError bugs.
    Using Pydantic means the payload is validated and IDE-autocompleted.
    """
    sub: str
    exp: datetime


def create_access_token(subject: str) -> str:
    """
    Signs a JWT with the shared secret.
    Uses timezone-aware UTC — datetime.utcnow() is deprecated in Python 3.12+.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": subject, "exp": expire},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def _decode_token(token: str) -> TokenPayload:
    """Private — decodes and validates the JWT, raises HTTP 401 on any failure."""
    try:
        raw = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return TokenPayload(**raw)
    except (JWTError, Exception):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """
    FastAPI dependency — add to any route that requires authentication:

        @router.get("/projects")
        def list_projects(user: str = Depends(get_current_user)):
            ...

    FastAPI calls this before the route function runs.
    Returns the subject (user identifier) from the token.
    Raises HTTP 401 automatically if the token is missing or invalid.
    """
    payload = _decode_token(credentials.credentials)
    if not payload.sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing subject claim",
        )
    return payload.sub
