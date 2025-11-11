# --- SMTP Email Service ---
"""
SMTP email sending implementation.
"""

from typing import Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
import json
import logging
from app.models.email_account import EmailAccount
from app.core.encryption import decrypt_token
from app.config import settings

logger = logging.getLogger(__name__)


async def send_via_smtp(
    email_account: EmailAccount,
    to_email: str,
    to_name: Optional[str],
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    tracking_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Send email via SMTP.
    
    Args:
        email_account: EmailAccount with SMTP configuration
        to_email: Recipient email address
        to_name: Recipient name (optional)
        subject: Email subject
        body: Plain text email body
        html_body: HTML email body (optional)
        tracking_id: Tracking ID for open tracking (optional)
        
    Returns:
        Dictionary with send result:
        - success: bool
        - message_id: str (SMTP message ID)
        - error: str (if failed)
    """
    if not email_account.smtp_config:
        return {
            "success": False,
            "message_id": None,
            "error": "SMTP configuration not found"
        }
    
    try:
        config = email_account.smtp_config
        
        # Decrypt password if encrypted
        password = config.get("encrypted_password", "")
        if password:
            try:
                password = decrypt_token(password)
            except Exception as e:
                logger.warning(f"Failed to decrypt SMTP password, using as-is: {str(e)}")
        
        # Create message
        message = MIMEMultipart("alternative")
        message["From"] = email_account.email_address
        message["To"] = to_email
        message["Subject"] = subject
        
        # Add tracking pixel to HTML body if provided
        if html_body and tracking_id:
            # Insert tracking pixel before closing body tag
            tracking_url = f"{settings.TRACKING_BASE_URL}/api/track-open/{tracking_id}"
            tracking_pixel = f'<img src="{tracking_url}" width="1" height="1" style="display:none;" />'
            if "</body>" in html_body.lower():
                html_body = html_body.replace("</body>", f"{tracking_pixel}</body>")
            else:
                html_body = html_body + tracking_pixel
        
        # Add plain text part
        text_part = MIMEText(body, "plain")
        message.attach(text_part)
        
        # Add HTML part if provided
        if html_body:
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)
        
        # Add tracking header if provided
        if tracking_id:
            message["X-Campaign-ID"] = str(tracking_id)
        
        # Connect and send
        host = config.get("host", "smtp.gmail.com")
        port = config.get("port", 587)
        use_tls = config.get("use_tls", True)
        username = config.get("username", email_account.email_address)
        
        async with aiosmtplib.SMTP(hostname=host, port=port, use_tls=use_tls) as smtp:
            await smtp.login(username, password)
            result = await smtp.send_message(message)
            
            # Extract message ID from result
            message_id = result.get("Message-Id", "") if result else None
            
            return {
                "success": True,
                "message_id": message_id,
                "error": None
            }
            
    except Exception as e:
        logger.error(f"SMTP send error: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message_id": None,
            "error": str(e)
        }

