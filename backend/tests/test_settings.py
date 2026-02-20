from app.core.settings import Settings


def test_database_url_encodes_special_characters_in_credentials() -> None:
    settings = Settings(
        pguser="postgres",
        pgpassword="Yassine1@;",
        pghost="localhost",
        pgport=5432,
        pgdatabase="mt_facturation",
    )
    assert settings.database_url == (
        "postgresql+psycopg://postgres:Yassine1%40%3B@localhost:5432/mt_facturation"
    )

