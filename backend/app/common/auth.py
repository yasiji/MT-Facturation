from collections.abc import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp

from app.common.errors import ApiException, build_error_response
from app.common.observability import get_request_id


class AuthContext(BaseModel):
    actor_id: str
    roles: list[str] = Field(default_factory=list)


DEFAULT_PUBLIC_PATHS = {
    "/",
    "/api/v1/health",
    "/docs",
    "/openapi.json",
    "/redoc",
}


def _parse_roles(raw_roles: str) -> list[str]:
    return [role.strip() for role in raw_roles.split(",") if role.strip()]


def _is_public_path(path: str, public_paths: set[str]) -> bool:
    if path in public_paths:
        return True
    return any(path.startswith(f"{public_path}/") for public_path in public_paths)


def _parse_bearer_token(token: str) -> AuthContext:
    # Local development format: actor_id:role1,role2
    if ":" not in token:
        return AuthContext(actor_id=token.strip(), roles=[])
    actor_id, raw_roles = token.split(":", 1)
    actor_id = actor_id.strip()
    if not actor_id:
        raise ValueError("Bearer token actor_id is missing")
    return AuthContext(actor_id=actor_id, roles=_parse_roles(raw_roles))


def extract_auth_context(request: Request) -> AuthContext | None:
    authorization = request.headers.get("Authorization", "")
    if authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        if not token:
            raise ValueError("Empty bearer token")
        return _parse_bearer_token(token)

    actor_id = request.headers.get("X-Actor-Id")
    if actor_id:
        roles = _parse_roles(request.headers.get("X-Actor-Roles", ""))
        return AuthContext(actor_id=actor_id.strip(), roles=roles)
    return None


def get_auth_context(request: Request) -> AuthContext:
    auth_context = getattr(request.state, "auth_context", None)
    if isinstance(auth_context, AuthContext):
        return auth_context
    raise ApiException(
        status_code=401,
        code="unauthorized",
        message="Authentication is required",
    )


def require_roles(required_roles: list[str]) -> Callable[[Request], AuthContext]:
    role_set = set(required_roles)

    def dependency(request: Request) -> AuthContext:
        auth_context = get_auth_context(request)
        if not role_set.issubset(set(auth_context.roles)):
            raise ApiException(
                status_code=403,
                code="forbidden",
                message="Insufficient permissions",
                details={"required_roles": sorted(role_set)},
            )
        return auth_context

    return dependency


class AuthContextMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        public_paths: set[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.public_paths = public_paths or DEFAULT_PUBLIC_PATHS

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == "OPTIONS":
            return await call_next(request)

        if _is_public_path(request.url.path, self.public_paths):
            return await call_next(request)

        try:
            auth_context = extract_auth_context(request)
        except ValueError as exc:
            return JSONResponse(
                status_code=401,
                content=build_error_response(
                    code="unauthorized",
                    message="Invalid authentication token format",
                    details={"reason": str(exc)},
                    trace_id=get_request_id(request),
                ),
            )

        if auth_context is None:
            return JSONResponse(
                status_code=401,
                content=build_error_response(
                    code="unauthorized",
                    message="Authentication is required",
                    details={},
                    trace_id=get_request_id(request),
                ),
            )

        request.state.auth_context = auth_context
        return await call_next(request)
