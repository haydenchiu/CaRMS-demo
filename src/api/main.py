"""FastAPI application for CaRMS data platform."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.utils.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting CaRMS Data Platform API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Test database connection
    from src.utils.database import test_connection
    if test_connection():
        logger.info("Database connection verified")
    else:
        logger.warning("Database connection failed - some endpoints may not work")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CaRMS Data Platform API")


# Initialize FastAPI app
app = FastAPI(
    title="CaRMS Residency Program Data Platform",
    description="Production-ready data platform for Canadian residency program information",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "name": "CaRMS Residency Program Data Platform",
        "version": "0.1.0",
        "status": "operational",
        "environment": settings.environment,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    from src.utils.database import test_connection
    
    db_status = "healthy" if test_connection() else "unhealthy"
    
    return {
        "status": "healthy",
        "database": db_status,
        "environment": settings.environment,
    }


# Import and include routers
from src.api.routes import programs, analytics

app.include_router(programs.router, prefix="/api/v1/programs", tags=["programs"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )
