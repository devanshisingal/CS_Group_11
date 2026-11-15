from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from backend.config import FRONTEND_DIR, get_database_url, get_session_secret
from backend.database import initialize_database, make_engine, make_session_factory
from backend.routers import accounts, authentication, secured


def create_app(database_url: str | None = None) -> FastAPI:
    engine = make_engine(database_url or get_database_url())
    session_factory = make_session_factory(engine)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        initialize_database(engine, session_factory)
        yield
        engine.dispose()

    application = FastAPI(title="SecureBank CSRF Lab", lifespan=lifespan)
    application.state.session_factory = session_factory
    application.add_middleware(
        SessionMiddleware,
        secret_key=get_session_secret(),
        session_cookie="securebank_session",
        same_site="lax",
        https_only=False,
        max_age=60 * 60,
    )
    application.include_router(authentication.router)
    application.include_router(accounts.router)
    application.include_router(secured.router)

    application.mount(
        "/static",
        StaticFiles(directory=str(FRONTEND_DIR)),
        name="static",
    )

    @application.get("/", include_in_schema=False)
    def dashboard_page() -> FileResponse:
        return FileResponse(Path(FRONTEND_DIR) / "dashboard.html")

    @application.get("/login", include_in_schema=False)
    def login_page() -> FileResponse:
        return FileResponse(Path(FRONTEND_DIR) / "login.html")

    return application


app = create_app()
