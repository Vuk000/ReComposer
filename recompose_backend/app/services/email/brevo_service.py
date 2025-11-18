# --- Brevo Email Service ---
"""
Brevo (formerly Sendinblue) email sending implementation.
Supports both SMTP and API methods.
"""

from typing import Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
import httpx
import logging
from app.config import settings
from app.models.email_account import EmailAccount

logger = logging.getLogger(__name__)


async def send_via_brevo_smtp(
    email_account: EmailAccount,
    to_email: str,
    to_name: Optional[str],
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    tracking_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Send email via Brevo SMTP.
    
    Args:
        email_account: EmailAccount with SMTP configuration (can use Brevo SMTP settings)
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
    # Use Brevo SMTP settings if configured
    smtp_server = settings.BREVO_SMTP_SERVER
    smtp_port = settings.BREVO_SMTP_PORT
    smtp_username = settings.BREVO_SMTP_USERNAME or email_account.email_address
    smtp_password = settings.BREVO_SMTP_PASSWORD
    
    if not smtp_password:
        return {
            "success": False,
            "message_id": None,
            "error": "Brevo SMTP password not configured"
        }
    
    try:
        # Create message
        if html_body:
            msg = MIMEMultipart("alternative")
            msg.attach(MIMEText(body, "plain"))
            # Insert tracking pixel if tracking_id provided
            if tracking_id:
                tracking_url = f"{settings.BACKEND_URL}/api/track-open/{tracking_id}"
                html_with_tracking = html_body + f'<img src="{tracking_url}" width="1" height="1" style="display:none;" />'
            else:
                html_with_tracking = html_body
            msg.attach(MIMEText(html_with_tracking, "html"))
        else:
            msg = MIMEText(body, "plain")
            # For plain text, we can't add tracking pixel, but we can add it to HTML version
            if tracking_id:
                # Convert to HTML and add tracking
                html_body = body.replace('\n', '<br>\n')
                msg = MIMEMultipart("alternative")
                msg.attach(MIMEText(body, "plain"))
                tracking_url = f"{settings.BACKEND_URL}/api/track-open/{tracking_id}"
                html_with_tracking = html_body + f'<img src="{tracking_url}" width="1" height="1" style="display:none;" />'
                msg.attach(MIMEText(html_with_tracking, "html"))
        
        msg["Subject"] = subject
        msg["From"] = email_account.email_address
        msg["To"] = to_email
        if to_name:
            msg["To"] = f"{to_name} <{to_email}>"
        
        # Send via SMTP
        await aiosmtplib.send(
            msg,
            hostname=smtp_server,
            port=smtp_port,
            username=smtp_username,
            password=smtp_password,
            use_tls=True,
        )
        
        message_id = msg["Message-ID"] or f"<{tracking_id or 'unknown'}@brevo>"
        
        logger.info(f"Email sent via Brevo SMTP to {to_email}")
        return {
            "success": True,
            "message_id": message_id,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Error sending email via Brevo SMTP: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message_id": None,
            "error": str(e)
        }


async def send_via_brevo_api(
    email_account: EmailAccount,
    to_email: str,
    to_name: Optional[str],
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    tracking_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Send email via Brevo Transactional API.
    
    Args:
        email_account: EmailAccount (email_address used as sender)
        to_email: Recipient email address
        to_name: Recipient name (optional)
        subject: Email subject
        body: Plain text email body
        html_body: HTML email body (optional)
        tracking_id: Tracking ID for open tracking (optional)
        
    Returns:
        Dictionary with send result:
        - success: bool
        - message_id: str (Brevo message ID)
        - error: str (if failed)
    """
    if not settings.BREVO_API_KEY:
        return {
            "success": False,
            "message_id": None,
            "error": "Brevo API key not configured"
        }
    
    try:
        # Prepare HTML body with tracking pixel
        final_html_body = html_body
        if not final_html_body:
            # Convert plain text to HTML
            final_html_body = body.replace('\n', '<br>\n')
        
        # Insert tracking pixel
        if tracking_id:
            tracking_url = f"{settings.BACKEND_URL}/api/track-open/{tracking_id}"
            final_html_body = final_html_body + f'<img src="{tracking_url}" width="1" height="1" style="display:none;" />'
        
        # Prepare request payload
        payload = {
            "sender": {
                "name": email_account.email_address.split("@")[0],
                "email": email_account.email_address
            },
            "to": [{
                "email": to_email,
                "name": to_name or to_email
            }],
            "subject": subject,
            "htmlContent": final_html_body,
            "textContent": body,
        }
        
        # Add tracking parameters
        if tracking_id:
            payload["headers"] = {
                "X-Tracking-ID": tracking_id
            }
        
        # Send via Brevo API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.brevo.com/v3/smtp/email",
                json=payload,
                headers={
                    "api-key": settings.BREVO_API_KEY,
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 201:
                result = response.json()
                message_id = result.get("messageId", f"brevo-{tracking_id or 'unknown'}")
                
                logger.info(f"Email sent via Brevo API to {to_email}, message_id={message_id}")
                return {
                    "success": True,
                    "message_id": message_id,
                    "error": None
                }
            else:
                error_msg = response.text
                logger.error(f"Brevo API error: {response.status_code} - {error_msg}")
                return {
                    "success": False,
                    "message_id": None,
                    "error": f"Brevo API error: {response.status_code} - {error_msg}"
                }
                
    except Exception as e:
        logger.error(f"Error sending email via Brevo API: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message_id": None,
            "error": str(e)
        }


async def send_via_brevo(
    email_account: EmailAccount,
    to_email: str,
    to_name: Optional[str],
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    tracking_id: Optional[str] = None,
    use_api: bool = True,
) -> Dict[str, Any]:
    """
    Send email via Brevo (prefers API, falls back to SMTP).
    
    Args:
        email_account: EmailAccount
        to_email: Recipient email address
        to_name: Recipient name (optional)
        subject: Email subject
        body: Plain text email body
        html_body: HTML email body (optional)
        tracking_id: Tracking ID for open tracking (optional)
        use_api: Whether to use API (True) or SMTP (False)
        
    Returns:
        Dictionary with send result
    """
    if use_api and settings.BREVO_API_KEY:
        return await send_via_brevo_api(
            email_account=email_account,
            to_email=to_email,
            to_name=to_name,
            subject=subject,
            body=body,
            html_body=html_body,
            tracking_id=tracking_id,
        )
    else:
        return await send_via_brevo_smtp(
            email_account=email_account,
            to_email=to_email,
            to_name=to_name,
            subject=subject,
            body=body,
            html_body=html_body,
            tracking_id=tracking_id,
        )

