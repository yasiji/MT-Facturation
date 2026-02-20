from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.common.auth import AuthContextMiddleware
from app.common.errors import register_exception_handlers
from app.common.observability import RequestContextMiddleware, configure_logging
from app.core.settings import get_settings
from app.db.session import initialize_schema

settings = get_settings()

configure_logging()
app = FastAPI(title=settings.app_name)
register_exception_handlers(app)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(AuthContextMiddleware, public_paths=settings.public_paths_set)
# Keep CORS middleware outermost so browser headers are present even for auth/errors.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins_list,
    allow_origin_regex=settings.cors_allow_origin_regex_value,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(v1_router)


@app.on_event("startup")
def startup() -> None:
    if settings.auto_create_schema:
        initialize_schema()


@app.get("/")
def root() -> dict[str, str]:
    return {"service": settings.app_name, "env": settings.app_env}
