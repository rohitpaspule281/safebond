from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import register_middleware
from app.core.runtime import start_background_model_warmup
from app.db.session import close_db_engine, init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(settings)
    if settings.db_auto_create_tables:
        await init_db()
    start_background_model_warmup()
    yield
    await close_db_engine()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Safebond backend foundation with modular FastAPI architecture, "
            "JWT authentication, PostgreSQL integration, ChromaDB integration, "
            "and operational health checks."
        ),
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_middleware(app)
    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/", tags=["meta"])
    async def root() -> dict[str, str]:
        return {
            "name": settings.app_name,
            "message": "Safebond backend is running.",
            "docs": "/docs",
            "version": settings.app_version,
        }

    return app


app = create_app()
