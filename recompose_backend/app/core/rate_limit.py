# --- Rate Limiting Middleware ---
"""
Rate limiting middleware using slowapi.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import settings
import logging
import time

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to apply rate limiting to specific routes."""
    
    def __init__(self, app, limiter: Limiter):
        super().__init__(app)
        self.limiter = limiter
        self.auth_limit = settings.RATE_LIMIT_AUTH_PER_MINUTE
        self.general_limit = settings.RATE_LIMIT_PER_MINUTE
        # Simple in-memory storage for rate limiting
        self._rate_limit_storage = {}
    
    def _check_rate_limit(self, key: str, limit: int, window: int = 60) -> bool:
        """Check if request is within rate limit."""
        current_time = time.time()
        window_start = current_time - window
        
        # Clean old entries
        if key in self._rate_limit_storage:
            self._rate_limit_storage[key] = [
                ts for ts in self._rate_limit_storage[key] if ts > window_start
            ]
        else:
            self._rate_limit_storage[key] = []
        
        # Check if limit exceeded
        if len(self._rate_limit_storage[key]) >= limit:
            return False
        
        # Add current request timestamp
        self._rate_limit_storage[key].append(current_time)
        return True
    
    async def dispatch(self, request: Request, call_next):
        """Apply rate limiting based on route."""
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        # Get client identifier
        key = get_remote_address(request)
        
        # Apply rate limiting based on path
        try:
            if request.url.path.startswith("/auth/"):
                # Auth endpoints have stricter limits
                if not self._check_rate_limit(f"auth:{key}", self.auth_limit):
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded: {self.auth_limit} requests per minute"
                    )
            elif request.url.path.startswith("/rewrite"):
                # Rewrite endpoints have general limits
                if not self._check_rate_limit(f"rewrite:{key}", self.general_limit):
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded: {self.general_limit} requests per minute"
                    )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            # Allow request through if rate limiting fails
            pass
        
        response = await call_next(request)
        return response

