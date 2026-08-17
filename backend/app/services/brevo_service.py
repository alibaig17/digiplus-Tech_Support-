"""
📧 Brevo (formerly Sendinblue) transactional email — used to deliver Email OTP codes.

Docs: https://developers.brevo.com/docs/send-a-transactional-email
"""
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from app.config import settings


def _get_client() -> sib_api_v3_sdk.TransactionalEmailsApi:
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = settings.brevo_api_key
    return sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))


def send_otp_email(to_email: str, to_name: str, otp: str) -> bool:
    """Send a 🔐 login OTP code via Brevo. Returns True on success."""
    # In dev mode without a Brevo key configured, just log to console so the
    # app is usable without a live account.
    if settings.dev_mode_log_otp or not settings.brevo_api_key:
        print(f"📧 [DEV MODE] OTP for {to_email}: {otp} (expires in {settings.otp_expire_minutes} min)")
        return True

    api_instance = _get_client()
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto;">
      <h2>🚀 AI Support Copilot</h2>
      <p>Hi {to_name or 'there'},</p>
      <p>Your one-time login code is:</p>
      <h1 style="letter-spacing: 6px; color:#7c3aed;">{otp}</h1>
      <p>This code expires in {settings.otp_expire_minutes} minutes. If you didn't request this, you can ignore this email.</p>
    </div>
    """
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to_email, "name": to_name or to_email}],
        sender={"email": settings.brevo_sender_email, "name": settings.brevo_sender_name},
        subject="🔐 Your AI Support Copilot login code",
        html_content=html_content,
    )
    try:
        api_instance.send_transac_email(send_smtp_email)
        return True
    except ApiException as e:
        print(f"❌ Brevo send failed: {e}")
        return False
