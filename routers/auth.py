from authx import AuthX, AuthXConfig
from schemas import UserLogin, UserRegister
from fastapi import HTTPException, APIRouter, Response
from database import async_engine
from sqlalchemy import select, insert
from models import users
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


@router.post("/register")
async def register(cred: UserRegister):
    async with async_engine.connect() as conn:
        existing = await conn.execute(
            select(users).where(users.c.email == cred.email)
        )
        if existing.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")

        await conn.execute(
            insert(users).values(
                email=cred.email,
                password_hash=hash_password(cred.password),
                role_id=ROLE_MAP[cred.role]  # ← maps role name to id
            )
        )
        await conn.commit()

    return {"message": "User registered successfully"}


@router.post("/register/admin")
async def register_admin(cred: UserRegister, admin_key: str):
    if admin_key != settings.ADMIN_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")

    async with async_engine.connect() as conn:
        existing = await conn.execute(
            select(users).where(users.c.email == cred.email)
        )
        if existing.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")

        await conn.execute(
            insert(users).values(
                email=cred.email,
                password_hash=hash_password(cred.password),
                role_id=ROLE_MAP["admin"]
            )
        )
        await conn.commit()

    return {"message": "Admin registered successfully"}


@router.post("/login")
async def login(cred: UserLogin, response: Response):
    async with async_engine.connect() as conn:
        result = await conn.execute(
            select(users).where(users.c.email == cred.email)
        )
        user = result.fetchone()

        if not user or not verify_password(cred.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = security.create_access_token(uid=str(user.id))
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)

    return {"access_token": token}