from backend.config import get_database_url
from backend.database import initialize_database, make_engine, make_session_factory
from backend import models


def main() -> None:
    database_url = get_database_url()
    if not database_url.startswith("sqlite:///"):
        raise SystemExit("reset_db.py only supports the configured SQLite database.")

    engine = make_engine(database_url)
    session_factory = make_session_factory(engine)

    models.Base.metadata.drop_all(bind=engine)
    initialize_database(engine, session_factory)
    engine.dispose()
    print(f"Reset demo database: {database_url}")


if __name__ == "__main__":
    main()
