import resend
import random
from datetime import datetime, timedelta
from sqlalchemy import insert
from database import async_engine
from models import email_verifications
from config import settings

resend.api_key = settings.RESEND_API_KEY

async def send_verification_code(user_id: int, email: str):
    code = str(random.randint(100000, 999999))
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    async with async_engine.connect() as conn:
        await conn.execute(
            insert(email_verifications).values(
                user_id=user_id,
                code=code,
                expires_at=expires_at,
            )
        )
        await conn.commit()

    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": email,
        "subject": "Tap.im — Verification Code",
        "text": f"Your verification code: {code}\nExpires in 10 minutes."
    })