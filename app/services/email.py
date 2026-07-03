"""Email delivery helpers for verification and password reset flows."""

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.config import get_settings

settings = get_settings()

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=settings.mail_starttls,
    MAIL_SSL_TLS=settings.mail_ssl_tls,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


async def send_verification_email(email: str, token: str, base_url: str) -> None:
    """Send an email with a link to verify the user's address."""
    verification_link = f"{base_url}/api/auth/verify/{token}"
    message = MessageSchema(
        subject="Підтвердження електронної пошти",
        recipients=[email],
        body=(
            "<p>Вітаємо!</p>"
            "<p>Для підтвердження електронної пошти перейдіть за посиланням:</p>"
            f'<p><a href="{verification_link}">{verification_link}</a></p>'
        ),
        subtype=MessageType.html,
    )
    fast_mail = FastMail(mail_config)
    await fast_mail.send_message(message)


async def send_password_reset_email(email: str, token: str, base_url: str) -> None:
    """Send an email with a link to reset the user's password."""
    reset_link = f"{base_url}/api/auth/reset-password/{token}"
    message = MessageSchema(
        subject="Скидання пароля",
        recipients=[email],
        body=(
            "<p>Ви запросили скидання пароля.</p>"
            "<p>Щоб встановити новий пароль, перейдіть за посиланням:</p>"
            f'<p><a href="{reset_link}">{reset_link}</a></p>'
            "<p>Якщо ви не робили цей запит, проігноруйте лист.</p>"
        ),
        subtype=MessageType.html,
    )
    fast_mail = FastMail(mail_config)
    await fast_mail.send_message(message)
