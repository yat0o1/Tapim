from fastapi import APIRouter, HTTPException
from sqlalchemy import select, update, delete
from database import async_engine
from models import companies
from schemas import CompanyUpdate

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get("/")
async def get_all_companies():
    async with async_engine.connect() as conn:
        result = await conn.execute(select(companies))
        return result.mappings().all()
    

@router.get("/{user_id}")
async def get_company(user_id: int):
    async with async_engine.connect() as conn:
        result = await conn.execute(
            select(companies).where(companies.c.user_id == user_id)
        )
        company = result.mappings().fetchone()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return company


@router.put("/{user_id}")
async def update_company(user_id: int, data: CompanyUpdate):
    values = {k: v for k, v in data.model_dump().items() if v is not None}
    async with async_engine.connect() as conn:
        await conn.execute(
            update(companies).where(companies.c.user_id == user_id).values(**values)
        )
        await conn.commit()
    return {"message": "Company updated"}


@router.delete("/{user_id}")
async def delete_company(user_id: int):
    async with async_engine.connect() as conn:
        await conn.execute(
            delete(companies).where(companies.c.user_id == user_id)
        )
        await conn.commit()
    return {"message": "Company deleted"}