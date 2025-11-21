# --- Authentication Router ---
"""
Authentication endpoints for user signup and login.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr, Field, field_validator, field_serializer, ConfigDict
from app.db import get_db
from app.models.user import User
from app.config import settings
import traceback
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)
import logging

# --- Router Setup ---
router = APIRouter(prefix="/auth", tags=["authentication"])

# --- Logger ---
logger = logging.getLogger(__name__)

# --- OAuth2 Scheme ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


# --- Pydantic Models ---
class UserSignup(BaseModel):
    """User signup request model."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128, description="Password must be 8-128 characters")
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(v) > 128:
            raise ValueError("Password must be at most 128 characters long")
        # Check for at least one letter and one number
        has_letter = any(c.isalpha() for c in v)
        has_number = any(c.isdigit() for c in v)
        if not (has_letter and has_number):
            raise ValueError("Password must contain at least one letter and one number")
        return v


class UserLogin(BaseModel):
    """User login request model."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response model."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User response model."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str
    created_at: datetime
    
    @field_serializer('created_at')
    def serialize_datetime(self, value: datetime) -> str:
        """Serialize datetime to ISO format string."""
        return value.isoformat()


# --- Authentication Dependency ---
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    sub_value = payload.get("sub")
    if sub_value is None:
        raise credentials_exception
    
    user_id: int = int(sub_value)
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


# --- Signup Endpoint ---
@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: Request, user_data: UserSignup, db: AsyncSession = Depends(get_db)):
    """
    Create a new user account.
    
    Args:
        request: FastAPI request object (for rate limiting)
        user_data: User signup data (email and password)
        db: Database session
        
    Returns:
        Created user object
        
    Raises:
        HTTPException: If email already exists
    """
    try:
        # Rate limiting is handled by middleware if enabled
        # --- Check if user already exists ---
        result = await db.execute(select(User).where(User.email == user_data.email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # --- Create new user ---
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        logger.info(
            f"User {new_user.id} signed up successfully",
            extra={"request_id": getattr(request.state, "request_id", "unknown")}
        )
        
        # Create and return access token
        access_token = create_access_token(data={"sub": str(new_user.id)})
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        logger.error(f"Signup error: {error_msg}\n{error_trace}", exc_info=True, extra={"request_id": getattr(request.state, "request_id", "unknown")})
        # Always show error in response for debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {error_msg}"
        )


# --- Login Endpoint ---
@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    
    Args:
        request: FastAPI request object (for rate limiting)
        login_data: User login data (email and password)
        db: Database session
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Rate limiting is handled by middleware if enabled
    # --- Find user by email ---
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # --- Create access token ---
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}


# --- Get Current User Endpoint ---
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user from dependency
        
    Returns:
        User information
    """
    return current_user


# --- Password Reset Endpoints ---
class ForgotPasswordRequest(BaseModel):
    """Forgot password request model."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request model."""
    token: str
    password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(v) > 128:
            raise ValueError("Password must be at most 128 characters long")
        has_letter = any(c.isalpha() for c in v)
        has_number = any(c.isdigit() for c in v)
        if not (has_letter and has_number):
            raise ValueError("Password must contain at least one letter and one number")
        return v


@router.post("/forgot-password")
async def forgot_password(
    request: Request,
    forgot_data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Request password reset email.
    
    Args:
        request: FastAPI request object
        forgot_data: Email address for password reset
        db: Database session
        
    Returns:
        Success message (always returns success to prevent email enumeration)
    """
    from datetime import timedelta
    import secrets
    
    # Find user by email
    result = await db.execute(select(User).where(User.email == forgot_data.email))
    user = result.scalar_one_or_none()
    
    if user:
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)  # Token valid for 1 hour
        
        user.password_reset_token = reset_token
        user.password_reset_expires = expires_at
        await db.commit()
        
        # Send reset email via Brevo (if configured)
        if settings.BREVO_API_KEY:
            try:
                from app.services.email.brevo_service import send_via_brevo_api
                from app.models.email_account import EmailAccount, EmailProvider
                
                # Create a temporary email account for sending
                temp_account = EmailAccount(
                    provider=EmailProvider.BREVO,
                    email_address=settings.BREVO_SMTP_USERNAME or "noreply@recompose.ai",
                    user_id=user.id
                )
                
                reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
                email_body = f"""
Hello,

You requested a password reset for your ReCompose account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
ReCompose Team
"""
                
                await send_via_brevo_api(
                    email_account=temp_account,
                    to_email=user.email,
                    to_name="",
                    subject="Reset Your ReCompose Password",
                    body=email_body,
                    html_body=email_body.replace('\n', '<br>\n')
                )
            except Exception as e:
                logger.error(f"Error sending password reset email: {str(e)}", exc_info=True)
                # Continue even if email fails
    
    # Always return success to prevent email enumeration
    return {"message": "If an account with that email exists, a password reset link has been sent."}


@router.post("/reset-password")
async def reset_password(
    request: Request,
    reset_data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password using reset token.
    
    Args:
        request: FastAPI request object
        reset_data: Reset token and new password
        db: Database session
        
    Returns:
        Success message
    """
    now = datetime.now(timezone.utc)
    
    # Find user by reset token
    result = await db.execute(
        select(User).where(
            User.password_reset_token == reset_data.token,
            User.password_reset_expires > now
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update password
    user.hashed_password = get_password_hash(reset_data.password)
    user.password_reset_token = None
    user.password_reset_expires = None
    await db.commit()
    
    logger.info(f"User {user.id} reset password successfully")
    
    return {"message": "Password reset successfully"}
