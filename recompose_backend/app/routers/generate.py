# --- Generate Router ---
"""
AI email generation endpoints for outreach campaigns (Pro plan only).
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from openai import AsyncOpenAI
from app.db import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.config import settings
from app.core.utils import retry_with_exponential_backoff
import logging

# --- Router Setup ---
router = APIRouter(prefix="/api/generate-email", tags=["generate"])

# --- Logger ---
logger = logging.getLogger(__name__)

# --- OpenAI Client ---
openai_client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    timeout=settings.OPENAI_TIMEOUT
)


# --- Pydantic Models ---
class GenerateEmailRequest(BaseModel):
    """Email generation request model."""
    contact_name: str = Field(..., min_length=1, max_length=255, description="Contact's name")
    contact_company: Optional[str] = Field(None, max_length=255, description="Contact's company")
    pitch_description: str = Field(..., min_length=10, max_length=2000, description="Brief description of the pitch")
    goal: Optional[str] = Field(None, max_length=500, description="Goal of the email (e.g., 'schedule a meeting', 'introduce product')")
    tone: Optional[str] = Field(default="professional", description="Tone: friendly, professional, or persuasive")
    
    @field_validator("tone")
    @classmethod
    def validate_tone(cls, v: str) -> str:
        """Validate tone is one of the allowed values."""
        valid_tones = ["friendly", "professional", "persuasive"]
        if v.lower() not in valid_tones:
            raise ValueError(f"Tone must be one of: {', '.join(valid_tones)}")
        return v.lower()


class GenerateEmailResponse(BaseModel):
    """Email generation response model."""
    subject: str
    body: str


# --- Endpoints ---
@router.post("", response_model=GenerateEmailResponse)
async def generate_email(
    request: Request,
    generate_request: GenerateEmailRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate an outreach email using AI (Pro plan only).
    
    Args:
        request: FastAPI request object
        generate_request: Generation request with contact and pitch details
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Generated email subject and body
        
    Raises:
        HTTPException: If user is not on Pro plan or OpenAI API fails
    """
    # Check Pro plan
    if current_user.subscription_plan != "pro":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email generation requires Pro plan"
        )
    
    # Validate OpenAI API key
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI API key is not configured"
        )
    
    # Construct prompt
    company_context = f" at {generate_request.contact_company}" if generate_request.contact_company else ""
    goal_context = f" Goal: {generate_request.goal}." if generate_request.goal else ""
    
    prompt = f"""You are a professional email outreach specialist. Generate a personalized outreach email.

Contact: {generate_request.contact_name}{company_context}
Pitch: {generate_request.pitch_description}{goal_context}
Tone: {generate_request.tone}

Generate a professional outreach email with:
1. A compelling subject line (max 80 characters)
2. A personalized email body that:
   - Addresses the contact by name
   - Introduces the pitch naturally
   - Is clear and concise
   - Maintains a {generate_request.tone} tone
   - Includes a clear call-to-action

Format your response as:
SUBJECT: [subject line]
BODY: [email body]"""
    
    try:
        # Call OpenAI API with retry logic
        async def call_openai():
            return await openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional email outreach specialist."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE,
            )
        
        if settings.OPENAI_MAX_RETRIES > 0:
            response = await retry_with_exponential_backoff(
                call_openai,
                max_retries=settings.OPENAI_MAX_RETRIES,
                initial_delay=settings.OPENAI_RETRY_DELAY
            )
        else:
            response = await call_openai()
        
        # Extract response
        if not response.choices or not response.choices[0].message.content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OpenAI API returned empty response"
            )
        
        content = response.choices[0].message.content.strip()
        
        # Parse subject and body
        subject = ""
        body = ""
        
        if "SUBJECT:" in content and "BODY:" in content:
            parts = content.split("BODY:")
            if len(parts) == 2:
                subject_part = parts[0].replace("SUBJECT:", "").strip()
                body = parts[1].strip()
                subject = subject_part
        elif content.startswith("SUBJECT:"):
            lines = content.split("\n")
            subject_line = lines[0].replace("SUBJECT:", "").strip()
            body = "\n".join(lines[1:]).strip()
            subject = subject_line
        else:
            # Fallback: use first line as subject, rest as body
            lines = content.split("\n")
            subject = lines[0].strip()[:80]  # Limit subject length
            body = "\n".join(lines[1:]).strip() if len(lines) > 1 else content
        
        # Ensure we have both subject and body
        if not subject:
            subject = "Follow-up"  # Default subject
        if not body:
            body = content  # Use full content as body
        
        logger.info(
            f"User {current_user.id} generated outreach email",
            extra={"request_id": getattr(request.state, "request_id", "unknown")}
        )
        
        return {
            "subject": subject,
            "body": body
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate email. Please try again later."
        )

