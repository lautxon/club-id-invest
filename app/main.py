"""
Club ID Invest - Main FastAPI Application
Fintech Investment Platform API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Runs on startup and shutdown.
    """
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Debug Mode: {settings.DEBUG}")
    
    # Initialize database (use Alembic for production migrations)
    if settings.DEBUG:
        init_db()
        print("Database initialized (DEBUG mode)")
    
    yield
    
    # Shutdown
    print(f"Shutting down {settings.APP_NAME}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Plataforma de inversion colectiva (Fideicomisos) con co-inversion automatica del Club",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health Check Endpoint
@app.get(f"{settings.API_PREFIX}/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# Root Endpoint
@app.get(f"{settings.API_PREFIX}/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Plataforma de inversion colectiva con co-inversion automatica",
        "docs": f"{settings.API_PREFIX}/docs",
        "health": f"{settings.API_PREFIX}/health",
    }


# =============================================================================
# INCLUDE ROUTERS (Commented out - to be implemented in Phase 3)
# =============================================================================
# from app.api import users, projects, investments, memberships, contracts, auth
# app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["Authentication"])
# app.include_router(users.router, prefix=f"{settings.API_PREFIX}/users", tags=["Users"])
# app.include_router(memberships.router, prefix=f"{settings.API_PREFIX}/memberships", tags=["Memberships"])
# app.include_router(projects.router, prefix=f"{settings.API_PREFIX}/projects", tags=["Projects"])
# app.include_router(investments.router, prefix=f"{settings.API_PREFIX}/investments", tags=["Investments"])
# app.include_router(contracts.router, prefix=f"{settings.API_PREFIX}/contracts", tags=["Contracts"])
