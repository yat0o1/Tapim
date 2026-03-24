from authx import AuthX, AuthXConfig
from schemas import (
    UserLogin,
    ApplicantRegister,
    RecruiterRegisterStep1,
    RecruiterRegisterStep2,
    VerifyEmail,
    ForgotPassword,
    ResetPassword
)
from fastapi import HTTPException, APIRouter, Response
from database import async_engine
from datetime import datetime
from sqlalchemy import select, insert, update, delete
from models import users, profiles, companies, email_verifications , roles
from auth_utils import hash_password, verify_password
from config import settings

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

config = AuthXConfig()
config.JWT_SECRET_KEY = settings.SECRET_KEY
config.JWT_ACCESS_COOKIE_NAME = "access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config=config)

ROLE_MAP = {
    "applicant": 1,
    "recruiter": 2,
    "admin": 3
}

@router.post("/register/applicant")
async def register_applicant(cred: ApplicantRegister):
    async with async_engine.connect() as conn:
        # проверка email
        existing = await conn.execute(
            select(users).where(users.c.email == cred.email)
        )
        if existing.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")

        # добавить в users
        result = await conn.execute(
            insert(users).values(
                email=cred.email,
                password_hash=hash_password(cred.password),
                role_id=ROLE_MAP["applicant"]
            ).returning(users.c.id)  # получить id нового юзера
        )
        new_user_id = result.scalar()

        # добавить в profiles
        await conn.execute(
            insert(profiles).values(
                user_id=new_user_id,
                first_name=cred.first_name,
                city=cred.city,
            )
        )
        await conn.commit()

    # отправить код верификации

    return {"message": "Registered successfully, check your email for verification code", "user_id": new_user_id}


@router.post("/register/recruiter/step1")
async def register_recruiter_step1(cred: RecruiterRegisterStep1):
    async with async_engine.connect() as conn:
        existing = await conn.execute(
            select(users).where(users.c.email == cred.email)
        )
        if existing.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")

        result = await conn.execute(
            insert(users).values(
                email=cred.email,
                password_hash=hash_password(cred.password),
                role_id=ROLE_MAP["recruiter"]
            ).returning(users.c.id)
        )
        new_user_id = result.scalar()

        await conn.execute(
            insert(profiles).values(
                user_id=new_user_id,
                first_name=cred.first_name,
            )
        )
        await conn.commit()


    return {"message": "Step 1 complete, check your email", "user_id": new_user_id}


@router.post("/register/recruiter/step2")
async def register_recruiter_step2(cred: RecruiterRegisterStep2):
    async with async_engine.connect() as conn:
        await conn.execute(
            insert(companies).values(
                user_id=cred.user_id,
                company_name=cred.company_name,
                company_size=cred.company_size,
                company_site=cred.company_site,
                user_role_in_company=cred.user_role_in_company,
            )
        )
        await conn.commit()

    return {"message": "Registration complete!"}

@router.post("/login")
async def login(cred: UserLogin, response: Response):
    async with async_engine.connect() as conn:
        result = await conn.execute(
            select(users, roles.c.name.label("role_name"))
            .join(roles, users.c.role_id == roles.c.id)
            .where(users.c.email == cred.email)
        )
        user = result.fetchone()

        if not user or not verify_password(cred.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = security.create_access_token(uid=str(user.id))
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)

    return {
        "access_token": token,
        "role": user.role_name  # "applicant", "recruiter", "admin"
    }

@router.post("/verify-email")
async def verify_email(data: VerifyEmail):
    async with async_engine.connect() as conn:
        result = await conn.execute(
            select(email_verifications).where(
                email_verifications.c.user_id == data.user_id,
                email_verifications.c.code == data.code,
                email_verifications.c.is_used == False,
                email_verifications.c.expires_at > datetime.utcnow()
            )
        )
        verification = result.fetchone()

        if not verification:
            raise HTTPException(status_code=400, detail="Invalid or expired code")

        # пометить код как использованный
        await conn.execute(
            update(email_verifications)
            .where(email_verifications.c.id == verification.id)
            .values(is_used=True)
        )
        await conn.commit()

    return {"message": "Email verified successfully"}


@router.post("/forgot-password")
async def forgot_password(data: ForgotPassword):
    async with async_engine.connect() as conn:
        result = await conn.execute(
            select(users).where(users.c.email == data.email)
        )
        user = result.fetchone()

        if not user:
            # не говорим что юзер не найден — безопасность
            return {"message": "If this email exists, a code has been sent"}


    return {"message": "If this email exists, a code has been sent"}


@router.post("/reset-password")
async def reset_password(data: ResetPassword):
    async with async_engine.connect() as conn:
        result = await conn.execute(
            select(email_verifications).where(
                email_verifications.c.user_id == data.user_id,
                email_verifications.c.code == data.code,
                email_verifications.c.is_used == False,
                email_verifications.c.expires_at > datetime.utcnow()
            )
        )
        verification = result.fetchone()

        if not verification:
            raise HTTPException(status_code=400, detail="Invalid or expired code")

        await conn.execute(
            update(users)
            .where(users.c.id == data.user_id)
            .values(password_hash=hash_password(data.new_password))
        )
        await conn.execute(
            update(email_verifications)
            .where(email_verifications.c.id == verification.id)
            .values(is_used=True)
        )
        await conn.commit()

    return {"message": "Password reset successfully"}