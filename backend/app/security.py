"""Auth + response-header controls."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user_id(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    """Phase 1 stub: accept any Bearer token as opaque dev identity.

    Phase 2: verify JWT signature/exp/iss/aud here, return `sub`.
    Fail closed when Authorization header is missing.
    """
    if creds is None or not creds.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
    return "dev-user"  # TODO(phase2): replace with verified JWT sub claim


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):  # type: ignore[no-untyped-def]
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response
