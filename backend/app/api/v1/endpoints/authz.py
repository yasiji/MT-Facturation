from typing import Annotated

from fastapi import APIRouter, Depends

from app.common.auth import AuthContext, get_auth_context, require_roles

router = APIRouter(tags=["auth"])


@router.get("/me")
def me(auth_context: Annotated[AuthContext, Depends(get_auth_context)]) -> dict[str, object]:
    return {
        "actor_id": auth_context.actor_id,
        "roles": auth_context.roles,
    }


@router.get("/admin/ping")
def admin_ping(
    auth_context: Annotated[AuthContext, Depends(require_roles(["admin"]))],
) -> dict[str, str]:
    return {"status": "ok", "actor_id": auth_context.actor_id}

