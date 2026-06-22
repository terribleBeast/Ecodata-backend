"""
Bearer-token middleware.

Extracts and validates a JWT from the Authorization header on every
request and stores decoded claims in ``request.state.token_claims``.

Invalid or missing tokens are silently ignored — individual endpoints
use ``require_auth`` to decide whether authentication is mandatory.
"""

from src.features.auth.service import decode_access_token
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                request.state.token_claims = decode_access_token(token)
            except Exception:
                pass  # invalid token → treat as unauthenticated
        response = await call_next(request)
        return response
