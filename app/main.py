from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from app.core.config import settings
from app.routes import dashboard, records, users
from app.utils.exceptions import generic_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: nothing needed (engine is created on import)
    yield
    from app.core.database import engine

    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Finance Data Processing & Access Control Backend.\n\n"
        "**Role-based access** is enforced via the `X-User-Id` header. "
        "The user is fetched from the database and their role is derived from `user.role`.\n\n"
        "Roles: `viewer` (dashboard only), `analyst` (read records + analytics), `admin` (full access).\n\n"
        "Run `uv run task seed` to bootstrap the initial admin user on a fresh database if you have decided to clone the repo and want to run it locally.\n\n"
        "**Evaluators:** An initial admin user is automatically created with this exact `X-User-Id`:\n"
        "`11111111-1111-1111-1111-111111111111`"
    ),
    lifespan=lifespan,
)

app.include_router(users.router)
app.include_router(records.router)
app.include_router(dashboard.router)

# Global exception handler for unhandled errors
app.add_exception_handler(Exception, generic_exception_handler)


@app.get("/", tags=["Health"])
async def health_check() -> dict:
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
