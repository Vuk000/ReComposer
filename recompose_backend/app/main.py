# --- Main Application Module ---
"""
FastAPI application entry point with CORS, middleware, and route registration.
"""

import logging
import json
import sys
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.routers import auth, rewrite, billing
from app.routers import contacts, campaigns, generate, tracking, user_settings, brevo_webhook, analytics


# --- Structured JSON Log Formatter ---
class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        return json.dumps(log_data)


# --- Configure Logging ---
if settings.LOG_FORMAT.lower() == "json":
    # Use JSON formatter for structured logging
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logging.basicConfig(
        level=logging.INFO if not settings.DEBUG else logging.DEBUG,
        handlers=[handler],
        force=True
    )
else:
    # Use text formatter for human-readable logs
    logging.basicConfig(
        level=logging.INFO if not settings.DEBUG else logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

logger = logging.getLogger(__name__)

# --- Application Lifecycle Events ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Rate limiting: {'enabled' if settings.RATE_LIMIT_ENABLED else 'disabled'}")
    logger.info(f"Log format: {settings.LOG_FORMAT}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")
    # Close database connections
    from app.db import engine
    await engine.dispose()
    logger.info("Database connections closed")

# --- Initialize FastAPI App ---
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for ReCompose AI - Email rewriting service",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# --- Rate Limiting Setup ---
# Initialize limiter (without app parameter - attach later)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Middleware Setup ---
from app.core.middleware import SecurityHeadersMiddleware, RequestIDMiddleware, RequestSizeLimitMiddleware
from app.core.rate_limit import RateLimitMiddleware as RateLimitMiddlewareImpl

# Add middleware in order: RequestID -> RequestSizeLimit -> RateLimit -> SecurityHeaders
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)
# Rate limiting middleware is always added but checks settings.RATE_LIMIT_ENABLED internally
app.add_middleware(RateLimitMiddlewareImpl, limiter=limiter)
app.add_middleware(SecurityHeadersMiddleware)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request Logging Middleware ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with request ID."""
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Create log record with request ID
    extra = {"request_id": request_id}
    logger.info(
        f"{request.method} {request.url.path}",
        extra=extra
    )
    
    response = await call_next(request)
    
    logger.info(
        f"Response status: {response.status_code}",
        extra=extra
    )
    
    return response


# --- Exception Handlers ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    # Convert errors to JSON-serializable format
    errors = exc.errors()
    serializable_errors = []
    for error in errors:
        serializable_error = {
            "loc": error.get("loc"),
            "msg": str(error.get("msg", "")),
            "type": error.get("type", ""),
        }
        # Include input if it's serializable
        if "input" in error:
            try:
                import json
                json.dumps(error["input"])
                serializable_error["input"] = error["input"]
            except (TypeError, ValueError):
                serializable_error["input"] = str(error["input"])
        serializable_errors.append(serializable_error)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": serializable_errors},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    # Show detailed error in DEBUG mode or if it's an HTTPException with detail
    error_detail = "Internal server error"
    if settings.DEBUG:
        import traceback
        error_detail = f"{str(exc)}\n{traceback.format_exc()}"
    elif isinstance(exc, HTTPException):
        error_detail = exc.detail
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": error_detail},
    )


# --- Health Check Endpoint ---
@app.get("/health")
async def health_check():
    """
    Health check endpoint with database connectivity check.
    Returns 503 Service Unavailable if database is disconnected.
    """
    from app.db import engine
    from sqlalchemy import text
    
    health_status = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "database": "unknown",
        "openai": "unknown",
        "redis": "unknown"
    }
    is_healthy = True
    
    # Check database connectivity
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status["database"] = "disconnected"
        is_healthy = False
    
    # Check OpenAI API key (if configured)
    if settings.OPENAI_API_KEY:
        health_status["openai"] = "configured"
    else:
        health_status["openai"] = "not_configured"
    
    # Check Redis/Celery (optional, don't fail health check)
    try:
        import redis
        redis_client = redis.from_url(settings.CELERY_BROKER_URL, socket_connect_timeout=1)
        redis_client.ping()
        health_status["redis"] = "connected"
    except Exception:
        health_status["redis"] = "not_available"
        # Redis is optional, don't fail health check
    
    status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content=health_status
    )


# --- Include Routers ---
app.include_router(auth.router)
app.include_router(rewrite.router)
app.include_router(billing.router)  # Always included, but returns 503 when BILLING_ENABLED=false
app.include_router(contacts.router)
app.include_router(campaigns.router)
app.include_router(generate.router)
app.include_router(tracking.router)
app.include_router(brevo_webhook.router)
app.include_router(analytics.router)
app.include_router(user_settings.router)


# --- Root Endpoint ---
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to ReCompose AI Backend",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

