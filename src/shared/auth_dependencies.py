"""
FastAPI dependencies for auth-protected endpoints.

``require_auth`` reads token claims placed on the request by
:class:`AuthMiddleware` and raises 401 if the user is not authenticated.

``require_auth_for_writes`` only enforces auth on mutating HTTP methods
(POST, PATCH, PUT, DELETE) — GET/HEAD/OPTIONS pass through unauthenticated.
"""

from fastapi import HTTPException, Request


async def require_auth(request: Request) -> dict:
    """Always require authentication."""
    claims = getattr(request.state, "token_claims", None)
    if claims is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return claims


async def require_auth_for_writes(request: Request) -> dict | None:
    """Require authentication only for mutating requests."""
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return None
    return await require_auth(request)
