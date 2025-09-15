from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from config.settings import settings
from src.api.routes import predictions, heatmap, advisories, simulation
from src.api.middleware import rate_limit_middleware, logging_middleware
from src.utils.database import init_database
from src.utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    logger.info("Starting 24-Hour Power Outage Forecasting System")
    await init_database()
    yield
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered early warning system for power outage prediction",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(rate_limit_middleware)
app.add_middleware(logging_middleware)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version
    }


# Metrics endpoint for Prometheus
@app.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Include API routes
app.include_router(predictions.router, prefix="/api/v1", tags=["Predictions"])
app.include_router(heatmap.router, prefix="/api/v1", tags=["Heatmap"])
app.include_router(advisories.router, prefix="/api/v1", tags=["Advisories"])
app.include_router(simulation.router, prefix="/api/v1", tags=["Simulation"])


@app.get("/", tags=["Root"])
async def read_root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the 24-Hour Power Outage Forecasting System",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "api_prefix": "/api/v1"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
