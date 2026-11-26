from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.config import settings
from app.core.logging import logger
from app.core.cache import cache_manager
from app.core.middleware import PerformanceTelemetryMiddleware
from app.core.rate_limit import RateLimitMiddleware
from app.db.base import Base
from app.db.session import engine
from app.api.router import api_router

# Import all models to ensure metadata registration
import app.db.models


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables & composite indexes...")
    Base.metadata.create_all(bind=engine)
    logger.info(f"{settings.APP_NAME} started successfully on environment: {settings.APP_ENV}")
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent supply chain risk forecasting & supplier document RAG intelligence advisory platform.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 1. Performance Telemetry & Profiling (X-Process-Time, X-Request-ID)
app.add_middleware(PerformanceTelemetryMiddleware)

# 2. Rate Limiting & Concurrency Guard (Sliding window IP-based throttling)
app.add_middleware(RateLimitMiddleware)

# 3. GZip response compression for high bandwidth efficiency (min 1KB payload)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 4. CORS configuration (Strictly bounded to authorized origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "cache": cache_manager.get_stats()
    }


@app.get("/api/v1/system/cache", tags=["System"])
def get_cache_stats():
    return {
        "status": "ok",
        "cache": cache_manager.get_stats()
    }


@app.post("/api/v1/system/cache/clear", tags=["System"])
def clear_all_caches():
    cache_manager.clear()
    return {"status": "ok", "message": "All in-memory caches cleared."}


@app.get("/", tags=["System"])
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR
    }
