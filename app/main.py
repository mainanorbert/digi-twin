"""FastAPI application factory and route registration."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import career


def _static_dir() -> Path | None:
    """
    Resolve the directory where the Next.js static export is stored, if present.

    Returns:
        Absolute path to a static frontend build, or ``None`` when unavailable.
    """
    project_root = Path(__file__).resolve().parent.parent
    candidates = (
        project_root / "static",
        project_root / "frontend" / "out",
    )
    return next((path for path in candidates if path.is_dir()), None)


def create_app() -> FastAPI:
    """
    Build the FastAPI application with routers and metadata.

    When a frontend static export exists, static files and ``index.html`` are
    served from ``/``.
    Otherwise ``GET /`` returns API hints.

    Returns:
        Configured FastAPI instance.
    """
    application = FastAPI(
        title="Digi-Twini API",
        version="0.3.0",
        description="LLM-powered career chat grounded in Norbert's professional profile and CV.",
    )
    application.include_router(career.router, prefix="/api/v1")

    @application.get("/health")
    def read_health() -> dict[str, str]:
        """Return service health status for probes and monitoring."""
        return {"status": "ok"}

    static_path = _static_dir()
    if static_path is not None:
        application.mount(
            "/",
            StaticFiles(directory=str(static_path), html=True),
            name="static",
        )
    else:

        @application.get("/")
        def read_root() -> dict[str, str]:
            """Return a short welcome when the frontend build is not present."""
            return {
                "message": "Digi-Twini API",
                "docs": "/docs",
                "career_chat": "POST /api/v1/career/chat",
                "career_stream": "POST /api/v1/career/chat/stream (SSE)",
            }

    return application


app = create_app()
