"""FastAPI application entrypoint."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler  # type: ignore
from slowapi.errors import RateLimitExceeded  # type: ignore
from slowapi.middleware import SlowAPIMiddleware  # type: ignore

from api.dependencies import limiter
from api.routes.analyze import router as analyze_router
from api.routes.report import router as report_router
from api.routes.analysis import router as analysis_router
from core.config import settings
from models.database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="ResumeAI API",
        description="AI-powered resume analysis: ATS scoring, resume fixes, career matching, and learning roadmaps.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(analyze_router, prefix="/api/v1", tags=["Analysis"])
    app.include_router(report_router, prefix="/api/v1", tags=["Report"])
    app.include_router(analysis_router, prefix="/api/v1", tags=["Analysis"])

    @app.on_event("startup")
    async def on_startup():
        logger.info("Initialising database...")
        await init_db()
        logger.info("ResumeAI API started. DB: %s | Redis: %s",
                    settings.database_url.split("///")[0],
                    "enabled" if settings.redis_enabled else "disabled")

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Check connectivity of DB, Redis, and HuggingFace API."""
        from utils.cache import cache_ping

        db_ok = False
        redis_ok = False
        hf_ok = False

        # DB check
        try:
            from models.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                await session.execute(__import__("sqlalchemy").text("SELECT 1"))
            db_ok = True
        except Exception as exc:
            logger.warning("DB health check failed: %s", exc)

        # Redis check
        try:
            redis_ok = await cache_ping()
        except Exception as exc:
            logger.warning("Redis health check failed: %s", exc)

        # HuggingFace API check (lightweight)
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://huggingface.co",
                    headers={"Authorization": f"Bearer {settings.hf_api_token}"},
                )
                hf_ok = resp.status_code < 500
        except Exception as exc:
            logger.warning("HF API health check failed: %s", exc)

        all_critical = db_ok
        status = "healthy" if all_critical else ("degraded" if (hf_ok or redis_ok) else "unhealthy")

        return JSONResponse(
            status_code=200 if all_critical else 503,
            content={
                "status": status,
                "db": db_ok,
                "redis": redis_ok,
                "redis_enabled": settings.redis_enabled,
                "hf_api": hf_ok,
            },
        )

    @app.get("/", tags=["Root"])
    async def root():
        return {"message": "ResumeAI API v1.0.0 — visit /docs for API documentation"}

    return app


app = create_app()
