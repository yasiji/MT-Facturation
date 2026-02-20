from functools import lru_cache
from urllib.parse import quote

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_LANDING_TOKEN_SECRET = "mt-facturation-landing-local-secret"


class Settings(BaseSettings):
    app_name: str = "MT-Facturation Backend"
    app_env: str = "local"
    app_port: int = 8000

    pghost: str = "localhost"
    pgport: int = 5432
    pguser: str = "postgres"
    pgpassword: str = "Yassine1@;"
    pgdatabase: str = "mt_facturation"
    public_paths: str = "/,/api/v1/health,/api/v1/landing,/docs,/openapi.json,/redoc"
    cors_allow_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174"
    )
    cors_allow_origin_regex: str = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"
    auto_create_schema: bool = False
    landing_token_secret: str = DEFAULT_LANDING_TOKEN_SECRET
    landing_lookup_token_ttl_seconds: int = 600
    landing_document_token_ttl_seconds: int = 86400
    contract_documents_dir: str = "generated/contracts"
    invoice_documents_dir: str = "generated/invoices"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    @model_validator(mode="after")
    def validate_security_defaults(self) -> "Settings":
        env = self.app_env.strip().lower()
        if (
            env not in {"local", "test"}
            and self.landing_token_secret == DEFAULT_LANDING_TOKEN_SECRET
        ):
            raise ValueError(
                "landing_token_secret must be overridden outside local/test environments",
            )
        return self

    @property
    def database_url(self) -> str:
        encoded_user = quote(self.pguser, safe="")
        encoded_password = quote(self.pgpassword, safe="")
        return (
            f"postgresql+psycopg://{encoded_user}:{encoded_password}"
            f"@{self.pghost}:{self.pgport}/{self.pgdatabase}"
        )

    @property
    def public_paths_set(self) -> set[str]:
        return {path.strip() for path in self.public_paths.split(",") if path.strip()}

    @property
    def cors_allow_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]

    @property
    def cors_allow_origin_regex_value(self) -> str | None:
        value = self.cors_allow_origin_regex.strip()
        return value if value else None


@lru_cache
def get_settings() -> Settings:
    return Settings()
