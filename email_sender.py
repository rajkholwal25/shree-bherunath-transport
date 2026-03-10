"""Send password reset email via Resend (free tier). No key = no send, app falls back to showing link on page."""
import resend
from config import RESEND_API_KEY, RESEND_FROM


def send_reset_email(to_email: str, reset_url: str, user_name: str = "") -> bool:
    """Send password reset link to the user. Returns True if sent, False if skipped or failed."""
    if not RESEND_API_KEY:
        return False
    resend.api_key = RESEND_API_KEY
    name = user_name or "there"
    html = f"""
    <p>Hi {name},</p>
    <p>You requested a password reset for Shree Bherunath Transport.</p>
    <p><a href="{reset_url}" style="background:#f59e0b;color:#111;padding:10px 18px;text-decoration:none;border-radius:8px;display:inline-block;">Reset password</a></p>
    <p>Or copy this link: <br><a href="{reset_url}">{reset_url}</a></p>
    <p>This link expires in 2 hours. If you didn't request this, ignore this email.</p>
    <p>— Shree Bherunath Transport</p>
    """
    try:
        resend.Emails.send({
            "from": RESEND_FROM,
            "to": [to_email],
            "subject": "Reset your password — Shree Bherunath Transport",
            "html": html,
        })
        return True
    except Exception:
        return False
