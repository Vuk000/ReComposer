# --- Rewrite Router ---
"""
Email rewrite endpoint using OpenAI GPT-4o.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from openai import AsyncOpenAI
from app.db import get_db
from app.models.user import User
from app.models.rewrite import RewriteLog
from app.core.utils import count_words, extract_tokens_from_usage
from app.routers.auth import get_current_user
from app.config import settings
import logging

# --- Router Setup ---
router = APIRouter(prefix="/rewrite", tags=["rewrite"])

# --- Logger ---
logger = logging.getLogger(__name__)

# --- OpenAI Client ---
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


# --- Pydantic Models ---
class RewriteRequest(BaseModel):
    """Email rewrite request model."""
    email_text: str
    tone: str  # friendly, professional, persuasive
    
    class Config:
        json_schema_extra = {
            "example": {
                "email_text": "Hey, I need this done ASAP!",
                "tone": "professional"
            }
        }


class RewriteResponse(BaseModel):
    """Email rewrite response model."""
    rewritten_email: str


# --- Rewrite Endpoint ---
@router.post("", response_model=RewriteResponse)
async def rewrite_email(
    request: RewriteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Rewrite an email using OpenAI GPT-4o.
    
    Args:
        request: Rewrite request with email text and tone
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Rewritten email text
        
    Raises:
        HTTPException: If OpenAI API fails or tone is invalid
    """
    # --- Validate tone ---
    valid_tones = ["friendly", "professional", "persuasive"]
    if request.tone not in valid_tones:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tone must be one of: {', '.join(valid_tones)}"
        )
    
    # --- Validate email text ---
    if not request.email_text or not request.email_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email text cannot be empty"
        )
    
    # --- Construct OpenAI prompt ---
    prompt = f"""You are a professional writing coach.

Rewrite the email below so it is clear, polite, and concise.
Preserve meaning and facts.
Tone of voice: {request.tone}
Output only the rewritten email text.

Email:
{request.email_text}"""
    
    try:
        # --- Call OpenAI API ---
        response = await openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a professional writing coach."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=settings.OPENAI_MAX_TOKENS,
            temperature=settings.OPENAI_TEMPERATURE,
        )
        
        # --- Extract rewritten email ---
        rewritten_email = response.choices[0].message.content.strip()
        
        # --- Extract usage information ---
        usage = response.usage
        token_used = extract_tokens_from_usage(usage.model_dump() if usage else None)
        
        # --- Count words in rewritten email ---
        word_count = count_words(rewritten_email)
        
        # --- Log rewrite to database ---
        rewrite_log = RewriteLog(
            user_id=current_user.id,
            tone=request.tone,
            word_count=word_count,
            token_used=token_used
        )
        
        db.add(rewrite_log)
        await db.commit()
        
        logger.info(
            f"User {current_user.id} rewrote email with tone '{request.tone}', "
            f"used {token_used} tokens"
        )
        
        return {"rewritten_email": rewritten_email}
        
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rewrite email: {str(e)}"
        )

