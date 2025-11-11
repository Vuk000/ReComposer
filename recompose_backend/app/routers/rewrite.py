# --- Rewrite Router ---
"""
Email rewrite endpoint using OpenAI GPT-4o.
"""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from pydantic import BaseModel, Field, field_validator, field_serializer, ConfigDict
from typing import List, Optional
from openai import AsyncOpenAI
from app.db import get_db
from app.models.user import User
from app.models.rewrite import RewriteLog
from app.core.utils import count_words, extract_tokens_from_usage, retry_with_exponential_backoff
from app.routers.auth import get_current_user
from app.config import settings
import logging

# --- Router Setup ---
router = APIRouter(prefix="/api/rewrite", tags=["rewrite"])

# --- Logger ---
logger = logging.getLogger(__name__)

# --- OpenAI Client ---
openai_client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    timeout=settings.OPENAI_TIMEOUT
)


# --- Pydantic Models ---
class RewriteRequest(BaseModel):
    """Email rewrite request model."""
    email_text: str = Field(..., min_length=1, max_length=10000, description="Email text to rewrite (1-10000 characters)")
    tone: str = Field(..., description="Tone: friendly, professional, or persuasive")
    
    @field_validator("email_text")
    @classmethod
    def validate_email_text(cls, v: str) -> str:
        """Validate email text length and content."""
        if not v or not v.strip():
            raise ValueError("Email text cannot be empty")
        if len(v) > 10000:
            raise ValueError("Email text cannot exceed 10000 characters")
        return v.strip()
    
    @field_validator("tone")
    @classmethod
    def validate_tone(cls, v: str) -> str:
        """Validate tone is one of the allowed values."""
        valid_tones = ["friendly", "professional", "persuasive"]
        if v.lower() not in valid_tones:
            raise ValueError(f"Tone must be one of: {', '.join(valid_tones)}")
        return v.lower()
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email_text": "Hey, I need this done ASAP!",
                "tone": "professional"
            }
        }
    )


class RewriteResponse(BaseModel):
    """Email rewrite response model."""
    rewritten_email: str


class RewriteLogResponse(BaseModel):
    """Rewrite log response model."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    original_email: str
    rewritten_email: str
    tone: str
    word_count: int
    token_used: int
    created_at: datetime
    
    @field_serializer('created_at')
    def serialize_datetime(self, value: datetime) -> str:
        """Serialize datetime to ISO format string."""
        return value.isoformat()


class RewriteLogsListResponse(BaseModel):
    """Paginated rewrite logs list response."""
    logs: List[RewriteLogResponse]
    total: int
    limit: int
    offset: int


class UsageResponse(BaseModel):
    """Usage statistics response model."""
    used: int
    limit: int
    remaining: int
    plan: str


# --- Helper Functions ---
async def get_daily_limit_for_user(user: User) -> int:
    """Get daily rewrite limit for a user based on their subscription plan."""
    if user.subscription_plan == "standard":
        return settings.STANDARD_PLAN_DAILY_LIMIT
    elif user.subscription_plan == "pro":
        return settings.PRO_PLAN_DAILY_LIMIT
    else:
        # Default to standard plan limit for unknown plans
        return settings.STANDARD_PLAN_DAILY_LIMIT


async def check_minute_usage_limit(user: User, db: AsyncSession) -> tuple[int, int]:
    """
    Check per-minute usage limit for a user (throttling).
    
    Args:
        user: User object
        db: Database session
        
    Returns:
        Tuple of (used_count_in_minute, limit_per_minute)
    """
    # Get per-minute limit (same for all plans, configurable)
    minute_limit = settings.REWRITE_RATE_LIMIT_PER_MINUTE
    
    # Calculate start of current minute
    now = datetime.now(timezone.utc)
    start_of_minute = now.replace(second=0, microsecond=0)
    
    # Count rewrites in the last minute
    count_result = await db.execute(
        select(func.count(RewriteLog.id))
        .where(RewriteLog.user_id == user.id)
        .where(RewriteLog.created_at >= start_of_minute)
    )
    used_count = count_result.scalar() or 0
    
    return used_count, minute_limit


async def check_daily_usage_limit(user: User, db: AsyncSession) -> tuple[int, int]:
    """
    Check daily usage limit for a user.
    Limits reset daily at UTC midnight.
    
    Args:
        user: User object
        db: Database session
        
    Returns:
        Tuple of (used_count, limit)
        
    Raises:
        HTTPException: If limit exceeded
    """
    # Get daily limit based on user's plan
    daily_limit = await get_daily_limit_for_user(user)
    
    # Calculate start of current UTC day (midnight UTC)
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Count rewrites since start of current UTC day
    count_result = await db.execute(
        select(func.count(RewriteLog.id))
        .where(RewriteLog.user_id == user.id)
        .where(RewriteLog.created_at >= start_of_day)
    )
    used_count = count_result.scalar() or 0
    
    return used_count, daily_limit


# --- Rewrite Endpoint ---
@router.post("", response_model=RewriteResponse)
async def rewrite_email(
    request: Request,
    rewrite_request: RewriteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Rewrite an email using OpenAI GPT-4o.
    
    Args:
        request: FastAPI request object (for request ID)
        rewrite_request: Rewrite request with email text and tone
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Rewritten email text
        
    Raises:
        HTTPException: If OpenAI API fails or tone is invalid
    """
    # Validation is handled by Pydantic validators above
    
    # --- Check per-minute throttling limit ---
    used_in_minute, minute_limit = await check_minute_usage_limit(current_user, db)
    if used_in_minute >= minute_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {minute_limit} rewrites per minute. Please slow down."
        )
    
    # --- Check daily usage limit ---
    used_count, daily_limit = await check_daily_usage_limit(current_user, db)
    if used_count >= daily_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily rewrite limit reached. You have used {used_count} of {daily_limit} rewrites today. "
                   f"Upgrade to Pro plan for higher limits."
        )
    
    # --- Validate OpenAI API key is set ---
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI API key is not configured. Please set OPENAI_API_KEY in your environment."
        )
    
    # --- Construct OpenAI prompt ---
    prompt = f"""You are a professional writing coach.

Rewrite the email below so it is clear, polite, and concise.
Preserve meaning and facts.
Tone of voice: {rewrite_request.tone}
Output only the rewritten email text.

Email:
{rewrite_request.email_text}"""
    
    try:
        # --- Call OpenAI API with retry logic ---
        async def call_openai():
            return await openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional writing coach."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE,
            )
        
        # Apply retry logic if enabled
        if settings.OPENAI_MAX_RETRIES > 0:
            response = await retry_with_exponential_backoff(
                call_openai,
                max_retries=settings.OPENAI_MAX_RETRIES,
                initial_delay=settings.OPENAI_RETRY_DELAY
            )
        else:
            response = await call_openai()
        
        # --- Extract rewritten email ---
        if not response.choices or not response.choices[0].message.content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OpenAI API returned empty response"
            )
        
        rewritten_email = response.choices[0].message.content.strip()
        
        # --- Extract usage information ---
        usage = response.usage
        token_used = extract_tokens_from_usage(usage.model_dump() if usage else None)
        
        # --- Count words in rewritten email ---
        word_count = count_words(rewritten_email)
        
        # --- Re-check usage limit right before committing (prevents race condition) ---
        used_count, daily_limit = await check_daily_usage_limit(current_user, db)
        if used_count >= daily_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Daily rewrite limit reached. You have used {used_count} of {daily_limit} rewrites today. "
                       f"Upgrade to Pro plan for higher limits."
            )
        
        # --- Log rewrite to database ---
        rewrite_log = RewriteLog(
            user_id=current_user.id,
            original_email=rewrite_request.email_text,
            rewritten_email=rewritten_email,
            tone=rewrite_request.tone,
            word_count=word_count,
            token_used=token_used
        )
        
        db.add(rewrite_log)
        await db.commit()
        
        logger.info(
            f"User {current_user.id} rewrote email with tone '{rewrite_request.tone}', "
            f"used {token_used} tokens",
            extra={"request_id": getattr(request.state, "request_id", "unknown")}
        )
        
        return {"rewritten_email": rewritten_email}
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the full error for debugging but don't expose internal details
        logger.error(f"OpenAI API error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rewrite email. Please try again later."
        )


# --- Get Rewrite Logs Endpoint ---
@router.get("/logs", response_model=RewriteLogsListResponse)
async def get_rewrite_logs(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100, description="Number of logs to return"),
    offset: int = Query(default=0, ge=0, description="Number of logs to skip")
):
    """
    Get paginated rewrite history for the current user.
    
    Args:
        request: FastAPI request object (for request ID logging)
        current_user: Current authenticated user
        db: Database session
        limit: Maximum number of logs to return (1-100, default: 20)
        offset: Number of logs to skip for pagination (default: 0)
        
    Returns:
        Paginated list of rewrite logs with metadata
    """
    # --- Get total count ---
    count_result = await db.execute(
        select(func.count(RewriteLog.id)).where(RewriteLog.user_id == current_user.id)
    )
    total = count_result.scalar() or 0
    
    # --- Get paginated logs ---
    result = await db.execute(
        select(RewriteLog)
        .where(RewriteLog.user_id == current_user.id)
        .order_by(desc(RewriteLog.created_at))
        .limit(limit)
        .offset(offset)
    )
    logs = result.scalars().all()
    
    logger.info(
        f"User {current_user.id} retrieved {len(logs)} rewrite logs "
        f"(offset: {offset}, limit: {limit}, total: {total})",
        extra={"request_id": getattr(request.state, "request_id", "unknown")}
    )
    
    return {
        "logs": logs,
        "total": total,
        "limit": limit,
        "offset": offset
    }


# --- Get Usage Statistics Endpoint ---
@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get daily usage statistics for the current user.
    
    Args:
        request: FastAPI request object (for request ID logging)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Usage statistics with used count, limit, remaining, and plan
    """
    used_count, daily_limit = await check_daily_usage_limit(current_user, db)
    remaining = max(0, daily_limit - used_count)
    
    logger.info(
        f"User {current_user.id} checked usage: {used_count}/{daily_limit} ({remaining} remaining)",
        extra={"request_id": getattr(request.state, "request_id", "unknown")}
    )
    
    return {
        "used": used_count,
        "limit": daily_limit,
        "remaining": remaining,
        "plan": current_user.subscription_plan
    }

