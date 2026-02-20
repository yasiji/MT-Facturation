from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import get_settings
from app.db.base import Base

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def initialize_schema() -> None:
    from app.models import billing, catalog, collections, contract, customer, landing  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _ensure_runtime_columns()


def _ensure_runtime_columns() -> None:
    # Local runtime safeguard while project still relies on create_all bootstrap.
    if engine.dialect.name != "postgresql":
        return

    statements = [
        "ALTER TABLE clients ADD COLUMN IF NOT EXISTS address VARCHAR(255)",
        "ALTER TABLE clients ADD COLUMN IF NOT EXISTS cin VARCHAR(40)",
        "ALTER TABLE clients ADD COLUMN IF NOT EXISTS is_delinquent BOOLEAN",
        "ALTER TABLE clients ADD COLUMN IF NOT EXISTS delinquent_since TIMESTAMPTZ",
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_clients_cin ON clients (cin) WHERE cin IS NOT NULL",
        "ALTER TABLE offers ADD COLUMN IF NOT EXISTS service_category VARCHAR(32)",
        "ALTER TABLE offers ADD COLUMN IF NOT EXISTS mobile_data_gb INTEGER",
        "ALTER TABLE offers ADD COLUMN IF NOT EXISTS mobile_calls_hours INTEGER",
        "ALTER TABLE offers ADD COLUMN IF NOT EXISTS internet_access_type VARCHAR(16)",
        "ALTER TABLE offers ADD COLUMN IF NOT EXISTS internet_fiber_speed_mbps INTEGER",
        "ALTER TABLE offers ADD COLUMN IF NOT EXISTS internet_adsl_speed_mbps INTEGER",
        "ALTER TABLE offers ADD COLUMN IF NOT EXISTS internet_landline_included BOOLEAN",
        "ALTER TABLE offers ADD COLUMN IF NOT EXISTS internet_tv_included BOOLEAN",
        "ALTER TABLE offers ADD COLUMN IF NOT EXISTS landline_national_included BOOLEAN",
        "ALTER TABLE offers ADD COLUMN IF NOT EXISTS landline_international_hours INTEGER",
        "ALTER TABLE offers ADD COLUMN IF NOT EXISTS landline_phone_hours INTEGER",
        "ALTER TABLE offers ADD COLUMN IF NOT EXISTS activation_fee NUMERIC(12,2)",
        (
            "UPDATE offers SET service_category = CASE "
            "WHEN service_type = 'mobile' THEN 'mobile' "
            "WHEN service_type IN ('fiber', 'adsl', 'tv', 'addon') THEN 'internet' "
            "WHEN service_type = 'landline' THEN 'landline' "
            "ELSE 'mobile' END "
            "WHERE service_category IS NULL OR length(trim(service_category)) = 0"
        ),
        (
            "UPDATE offers SET internet_landline_included = FALSE "
            "WHERE internet_landline_included IS NULL"
        ),
        (
            "UPDATE offers SET internet_landline_included = TRUE "
            "WHERE service_category = 'internet' "
            "AND internet_landline_included IS DISTINCT FROM TRUE"
        ),
        "UPDATE offers SET internet_tv_included = FALSE WHERE internet_tv_included IS NULL",
        (
            "UPDATE offers SET landline_national_included = FALSE "
            "WHERE landline_national_included IS NULL"
        ),
        "UPDATE offers SET activation_fee = 0 WHERE activation_fee IS NULL",
        "ALTER TABLE offers ALTER COLUMN service_category SET DEFAULT 'mobile'",
        "UPDATE clients SET is_delinquent = FALSE WHERE is_delinquent IS NULL",
        "ALTER TABLE offers ALTER COLUMN service_category SET NOT NULL",
        "ALTER TABLE clients ALTER COLUMN is_delinquent SET DEFAULT FALSE",
        "ALTER TABLE clients ALTER COLUMN is_delinquent SET NOT NULL",
        "ALTER TABLE offers ALTER COLUMN internet_landline_included SET DEFAULT FALSE",
        "ALTER TABLE offers ALTER COLUMN internet_tv_included SET DEFAULT FALSE",
        "ALTER TABLE offers ALTER COLUMN landline_national_included SET DEFAULT FALSE",
        "ALTER TABLE offers ALTER COLUMN activation_fee SET DEFAULT 0",
        "ALTER TABLE offers ALTER COLUMN internet_landline_included SET NOT NULL",
        "ALTER TABLE offers ALTER COLUMN internet_tv_included SET NOT NULL",
        "ALTER TABLE offers ALTER COLUMN landline_national_included SET NOT NULL",
        "ALTER TABLE offers ALTER COLUMN activation_fee SET NOT NULL",
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
