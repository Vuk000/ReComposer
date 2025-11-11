# --- Email Sender Module ---
"""
Abstract email sending interface that routes to different providers.
"""

from typing import Optional, Dict, Any
from app.models.email_account import EmailAccount, EmailProvider
from app.models.contact import Contact
from app.models.campaign_email import CampaignEmail
from app.services.email.smtp_service import send_via_smtp
# Import Gmail and Outlook services (may not be fully implemented yet)
try:
    from app.services.email.gmail_service import send_via_gmail
except ImportError:
    send_via_gmail = None

try:
    from app.services.email.outlook_service import send_via_outlook
except ImportError:
    send_via_outlook = None
import logging

logger = logging.getLogger(__name__)


def merge_template(template: str, contact: Contact, **kwargs) -> str:
    """
    Merge email template with contact data.
    
    Replaces placeholders like {{Name}}, {{Company}}, {{Email}} with actual values.
    Also supports additional kwargs for custom placeholders.
    
    Args:
        template: Email template with placeholders
        contact: Contact object with data
        **kwargs: Additional placeholder values
        
    Returns:
        Merged email content
    """
    merged = template
    
    # Standard placeholders
    placeholders = {
        "Name": contact.name or "",
        "Company": contact.company or "",
        "Email": contact.email or "",
        "First Name": contact.name.split()[0] if contact.name else "",
    }
    
    # Add custom placeholders from kwargs
    placeholders.update({k: str(v) for k, v in kwargs.items()})
    
    # Replace placeholders
    for key, value in placeholders.items():
        merged = merged.replace(f"{{{{{key}}}}}", value)
        merged = merged.replace(f"{{{{ {key} }}}}", value)  # Support {{ Name }} format too
    
    return merged


async def send_email(
    email_account: EmailAccount,
    to_email: str,
    to_name: Optional[str],
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    campaign_id: Optional[int] = None,
    tracking_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Send an email using the appropriate provider.
    
    This is the main entry point for sending emails. It routes to the
    appropriate provider-specific implementation.
    
    Args:
        email_account: EmailAccount with provider configuration
        to_email: Recipient email address
        to_name: Recipient name (optional)
        subject: Email subject
        body: Plain text email body
        html_body: HTML email body (optional)
        campaign_id: Campaign ID for tracking (optional)
        tracking_id: Tracking ID for open tracking (optional)
        
    Returns:
        Dictionary with send result:
        - success: bool
        - message_id: str (provider message ID)
        - error: str (if failed)
    """
    try:
        if email_account.provider == EmailProvider.SMTP:
            result = await send_via_smtp(
                email_account=email_account,
                to_email=to_email,
                to_name=to_name,
                subject=subject,
                body=body,
                html_body=html_body,
                tracking_id=tracking_id,
            )
        elif email_account.provider == EmailProvider.GMAIL:
            if send_via_gmail is None:
                raise ValueError("Gmail service not available")
            result = await send_via_gmail(
                email_account=email_account,
                to_email=to_email,
                to_name=to_name,
                subject=subject,
                body=body,
                html_body=html_body,
                tracking_id=tracking_id,
            )
        elif email_account.provider == EmailProvider.OUTLOOK:
            if send_via_outlook is None:
                raise ValueError("Outlook service not available")
            result = await send_via_outlook(
                email_account=email_account,
                to_email=to_email,
                to_name=to_name,
                subject=subject,
                body=body,
                html_body=html_body,
                tracking_id=tracking_id,
            )
        else:
            raise ValueError(f"Unsupported email provider: {email_account.provider}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error sending email via {email_account.provider}: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message_id": None,
            "error": str(e)
        }

