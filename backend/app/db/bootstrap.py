import psycopg
from psycopg import sql

from app.core.settings import get_settings
from app.db.session import initialize_schema


def ensure_database_exists() -> bool:
    settings = get_settings()
    created = False

    with psycopg.connect(
        host=settings.pghost,
        port=settings.pgport,
        user=settings.pguser,
        password=settings.pgpassword,
        dbname="postgres",
        autocommit=True,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (settings.pgdatabase,),
            )
            exists = cursor.fetchone() is not None
            if not exists:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(sql.Identifier(settings.pgdatabase)),
                )
                created = True

    return created


def main() -> None:
    created = ensure_database_exists()
    initialize_schema()
    if created:
        print("DB bootstrap: database created and schema initialized.")
    else:
        print("DB bootstrap: database already existed, schema checked/initialized.")


if __name__ == "__main__":
    main()

