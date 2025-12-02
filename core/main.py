from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi.errors import RateLimitExceeded

from core.api import notes, payment
from core.middleware import error_handler_middleware, logging_middleware
from core.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from shared.utils.logger import get_logger

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TubeWiki Core API",
    description="Backend API for TubeWiki - YouTube video summarization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://*",
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.middleware("http")(logging_middleware)
app.middleware("http")(error_handler_middleware)

# Include routers
app.include_router(notes.router, prefix="/api/v1", tags=["Notes"])
app.include_router(payment.router, prefix="/api/v1", tags=["Payment"])

# Health check endpoint
@app.get("/healthz", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "ok",
        "service": "core-api",
        "version": "1.0.0"
    }

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "TubeWiki Core API",
        "docs": "/docs",
        "health": "/healthz"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 TubeWiki Core API starting up...")
    logger.info("📚 API documentation available at /docs")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 TubeWiki Core API shutting down...")

