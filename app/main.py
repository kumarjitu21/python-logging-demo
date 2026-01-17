"""Main FastAPI application with logging integration."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import LoggingMiddleware
from app.api.routes import router

# Initialize logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown."""
    # Startup
    logger.info(
        "Application starting up",
        app_name=settings.app_name,
        version=settings.version,
        debug=settings.debug,
        log_level=settings.log_level,
    )
    yield
    # Shutdown
    logger.info(
        "Application shutting down",
        app_name=settings.app_name,
    )


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="FastAPI application with industry-best-practice logging using Loguru",
    version=settings.version,
    debug=settings.debug,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom logging middleware
app.add_middleware(LoggingMiddleware)


# Include routers
app.include_router(router, prefix="/api", tags=["API"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    logger.info("Root endpoint accessed")
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.version,
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
