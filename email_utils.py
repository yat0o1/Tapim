from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from config import settings
import random
from datetime import datetime, timedelta
from sqlalchemy import insert, select, update
from database import async_engine
from models import email_verifications, users

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)

async def send_verification_code(user_id: int, email: str):
    code = str(random.randint(100000, 999999))  # 6-значный код
    expires_at = datetime.utcnow() + timedelta(minutes=10)  # код живет 10 минут

    async with async_engine.connect() as conn:
        await conn.execute(
            insert(email_verifications).values(
                user_id=user_id,
                code=code,
                expires_at=expires_at,
            )
        )
        await conn.commit()

    message = MessageSchema(
        subject="Tap.im — Verification Code",
        recipients=[email],
        body=f"Your verification code: {code}\nExpires in 10 minutes.",
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)