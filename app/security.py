from __future__ import annotations

import hmac
import time
from hashlib import sha256

from fastapi import Request

from app.config import settings

COOKIE_NAME = "tracker_session"


def auth_enabled() -> bool:
    return bool(settings.AUTH_PASSWORD)


def _secret() -> str:
    return settings.SESSION_SECRET or settings.AUTH_PASSWORD or "dev-only"


def _sign(username: str, expires_at: int) -> str:
    payload = f"{username}:{expires_at}"
    return hmac.new(_secret().encode("utf-8"), payload.encode("utf-8"), sha256).hexdigest()


def create_session_cookie(username: str) -> str:
    expires_at = int(time.time() + max(settings.SESSION_DAYS, 1) * 86400)
    signature = _sign(username, expires_at)
    return f"{username}:{expires_at}:{signature}"


def valid_session_cookie(value: str | None) -> bool:
    if not auth_enabled():
        return True
    if not value:
        return False

    try:
        username, expires_text, signature = value.split(":", 2)
        expires_at = int(expires_text)
    except ValueError:
        return False

    if username != settings.AUTH_USERNAME or expires_at < int(time.time()):
        return False

    expected = _sign(username, expires_at)
    return hmac.compare_digest(signature, expected)


def valid_login(username: str, password: str) -> bool:
    if not auth_enabled():
        return True
    username_ok = hmac.compare_digest(username, settings.AUTH_USERNAME)
    password_ok = hmac.compare_digest(password, settings.AUTH_PASSWORD or "")
    return username_ok and password_ok


def request_is_authenticated(request: Request) -> bool:
    return valid_session_cookie(request.cookies.get(COOKIE_NAME))
