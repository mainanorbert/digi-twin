"""FastAPI application factory and route registration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.deps import get_settings
from app.routers import career


def create_app() -> FastAPI:
    """
    Build the FastAPI application with routers and metadata.

    Returns:
        Configured FastAPI instance.
    """
    settings = get_settings()
    application = FastAPI(
        title="Digi-Twini API",
        version="0.3.0",
        description="LLM-powered career chat grounded in Norbert's professional profile and CV.",
    )
    cors_origins = settings.cors_allowed_origins_list()
    if cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    application.include_router(career.router, prefix="/api/v1")

    @application.get("/health")
    def read_health() -> dict[str, str]:
        """Return service health status for probes and monitoring."""
        return {"status": "ok"}

    @application.get("/")
    def read_root() -> dict[str, str]:
        """Return a short welcome for the standalone API service."""
        return {
            "message": "Digi-Twini API",
            "docs": "/docs",
            "career_chat": "POST /api/v1/career/chat",
            "career_stream": "POST /api/v1/career/chat/stream (SSE)",
        }

    return application


app = create_app()
