# --- Gmail Email Service ---
"""
Gmail API email sending implementation (structure only, defer full OAuth).
"""

from typing import Optional, Dict, Any
import logging
from app.models.email_account import EmailAccount

logger = logging.getLogger(__name__)


async def send_via_gmail(
    email_account: EmailAccount,
    to_email: str,
    to_name: Optional[str],
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    tracking_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Send email via Gmail API.
    
    TODO: Implement full OAuth flow and Gmail API integration.
    For now, returns a placeholder error.
    
    Args:
        email_account: EmailAccount with Gmail configuration
        to_email: Recipient email address
        to_name: Recipient name (optional)
        subject: Email subject
        body: Plain text email body
        html_body: HTML email body (optional)
        tracking_id: Tracking ID for open tracking (optional)
        
    Returns:
        Dictionary with send result
    """
    logger.warning("Gmail API integration not yet implemented")
    return {
        "success": False,
        "message_id": None,
        "error": "Gmail API integration not yet implemented"
    }


async def check_replies_gmail(email_account: EmailAccount, since_timestamp: Optional[str] = None) -> list:
    """
    Check for replies via Gmail API.
    
    TODO: Implement Gmail API polling using historyId or search.
    
    Args:
        email_account: EmailAccount with Gmail configuration
        since_timestamp: Timestamp to check since (ISO format)
        
    Returns:
        List of reply message IDs
    """
    logger.warning("Gmail reply detection not yet implemented")
    return []


async def refresh_token_gmail(email_account: EmailAccount) -> bool:
    """
    Refresh Gmail OAuth token.
    
    TODO: Implement token refresh using refresh token.
    
    Args:
        email_account: EmailAccount with Gmail configuration
        
    Returns:
        True if refresh successful
    """
    logger.warning("Gmail token refresh not yet implemented")
    return False

