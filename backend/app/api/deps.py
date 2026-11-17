import hmac

from fastapi import Header, HTTPException, status

from app.core.config import get_settings


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    expected = get_settings().admin_api_token
    if not x_admin_token or not hmac.compare_digest(x_admin_token, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin token")
