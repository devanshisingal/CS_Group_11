from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from starlette.requests import Request


class Base(DeclarativeBase):
    pass


def make_engine(database_url: str) -> Engine:
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    engine = create_engine(database_url, connect_args=connect_args)

    if database_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def enable_foreign_keys(connection, _record) -> None:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db(request: Request) -> Generator[Session, None, None]:
    session_factory = request.app.state.session_factory
    with session_factory() as session:
        yield session


def initialize_database(engine: Engine, session_factory: sessionmaker[Session]) -> None:
    from backend import models
    from backend.auth import hash_password

    Base.metadata.create_all(bind=engine)
    with session_factory() as session:
        if session.query(models.Account).count() == 0:
            session.add_all(
                [
                    models.Account(
                        username="alice",
                        password_hash=hash_password("password123"),
                        balance_paise=1_000_000,
                    ),
                    models.Account(
                        username="attacker",
                        password_hash=hash_password("attacker123"),
                        balance_paise=0,
                    ),
                ]
            )
            session.commit()
