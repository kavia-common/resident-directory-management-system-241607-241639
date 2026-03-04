from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.core.db import init_db_schema
from src.api.routes.auth import router as auth_router
from src.api.routes.residents import router as residents_router

openapi_tags = [
    {"name": "Health", "description": "Service health and readiness endpoints."},
    {"name": "Auth", "description": "Admin authentication endpoints (login + token validation)."},
    {"name": "Residents", "description": "Resident directory endpoints (public list/search + admin management)."},
]

app = FastAPI(
    title="Resident Directory Backend API",
    description=(
        "FastAPI backend for the Resident Directory app.\n\n"
        "Auth: Use `POST /auth/login` to obtain a Bearer JWT, then pass it as "
        "`Authorization: Bearer <token>` for protected endpoints."
    ),
    version="1.0.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _on_startup() -> None:
    """Initialize DB schema on startup.

    Note: For production, prefer migrations (Alembic). For this project we create tables
    automatically to simplify environment bootstrapping.

    Preview environment note:
    The DB container may not be reachable immediately. We avoid crashing the app on boot
    so port readiness can succeed; DB-backed endpoints will still error until DB is up.
    """
    try:
        init_db_schema()
    except Exception:
        # Intentionally tolerant: health endpoint should remain available.
        # The orchestrator/CI will surface DB connectivity issues separately.
        return


@app.get(
    "/",
    tags=["Health"],
    summary="Health check",
    description="Basic health check endpoint.",
    operation_id="health_check",
)
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}


app.include_router(auth_router)
app.include_router(residents_router)
