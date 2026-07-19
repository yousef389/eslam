from __future__ import annotations

import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.infrastructure.cache import redis_client

GLOBAL_RATE_LIMIT = 60
GLOBAL_RATE_WINDOW = 60

LOGIN_RATE_LIMIT = 10
LOGIN_RATE_WINDOW = 60

LOGIN_PATH = "/api/v1/auth/login"
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 1800


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path

        is_login = path == LOGIN_PATH

        if is_login:
            key = f"rate_limit:login:{client_ip}"
            limit = LOGIN_RATE_LIMIT
            window = LOGIN_RATE_WINDOW
        else:
            key = f"rate_limit:global:{client_ip}"
            limit = GLOBAL_RATE_LIMIT
            window = GLOBAL_RATE_WINDOW

        try:
            current = await redis_client.incr(key)
            if current == 1:
                await redis_client.expire(key, window)

            if current > limit:
                ttl = await redis_client.ttl(key)
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded. Try again later."},
                    headers={"Retry-After": str(max(ttl, 1))},
                )
        except Exception:
            pass

        response = await call_next(request)
        return response


class AccountLockoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path != LOGIN_PATH or request.method != "POST":
            return await call_next(request)

        try:
            body = await request.body()
            import json

            data = json.loads(body) if body else {}
            username = data.get("username", "").strip().lower()

            if username:
                lock_key = f"account_lockout:{username}"
                is_locked = await redis_client.exists(lock_key)

                if is_locked:
                    ttl = await redis_client.ttl(lock_key)
                    return JSONResponse(
                        status_code=423,
                        content={
                            "detail": "Account temporarily locked due to too many failed login attempts.",
                            "retry_after": ttl,
                        },
                        headers={"Retry-After": str(ttl)},
                    )
        except Exception:
            pass

        return await call_next(request)
