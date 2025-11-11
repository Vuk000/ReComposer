# --- Outlook Email Service ---
"""
Microsoft Graph API email sending implementation (structure only, defer full OAuth).
"""

from typing import Optional, Dict, Any
import logging
from app.models.email_account import EmailAccount

logger = logging.getLogger(__name__)


async def send_via_outlook(
    email_account: EmailAccount,
    to_email: str,
    to_name: Optional[str],
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    tracking_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Send email via Microsoft Graph API.
    
    TODO: Implement full OAuth flow and Microsoft Graph API integration.
    For now, returns a placeholder error.
    
    Args:
        email_account: EmailAccount with Outlook configuration
        to_email: Recipient email address
        to_name: Recipient name (optional)
        subject: Email subject
        body: Plain text email body
        html_body: HTML email body (optional)
        tracking_id: Tracking ID for open tracking (optional)
        
    Returns:
        Dictionary with send result
    """
    logger.warning("Outlook API integration not yet implemented")
    return {
        "success": False,
        "message_id": None,
        "error": "Outlook API integration not yet implemented"
    }


async def check_replies_outlook(email_account: EmailAccount, since_timestamp: Optional[str] = None) -> list:
    """
    Check for replies via Microsoft Graph API.
    
    TODO: Implement Microsoft Graph API polling using delta queries.
    
    Args:
        email_account: EmailAccount with Outlook configuration
        since_timestamp: Timestamp to check since (ISO format)
        
    Returns:
        List of reply message IDs
    """
    logger.warning("Outlook reply detection not yet implemented")
    return []


async def refresh_token_outlook(email_account: EmailAccount) -> bool:
    """
    Refresh Outlook OAuth token.
    
    TODO: Implement token refresh using refresh token.
    
    Args:
        email_account: EmailAccount with Outlook configuration
        
    Returns:
        True if refresh successful
    """
    logger.warning("Outlook token refresh not yet implemented")
    return False

