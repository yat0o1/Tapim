from fastapi import APIRouter, HTTPException
from sqlalchemy import select, insert, delete
from database import async_engine
from models import favorites, vacancies

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.post("/{user_id}/{vacancy_id}")
async def add_favorite(user_id: int, vacancy_id: str):
    async with async_engine.connect() as conn:
        # проверить не добавлена ли уже
        existing = await conn.execute(
            select(favorites).where(
                favorites.c.user_id == user_id,
                favorites.c.vacancy_id == vacancy_id
            )
        )
        if existing.fetchone():
            raise HTTPException(status_code=400, detail="Already in favorites")

        await conn.execute(
            insert(favorites).values(
                user_id=user_id,
                vacancy_id=vacancy_id
            )
        )
        await conn.commit()
    return {"message": "Added to favorites"}


@router.get("/{user_id}")
async def get_favorites(user_id: int):
    async with async_engine.connect() as conn:
        result = await conn.execute(
            select(vacancies)
            .join(favorites, vacancies.c.id == favorites.c.vacancy_id)
            .where(favorites.c.user_id == user_id)
        )
        return result.mappings().all()


@router.delete("/{user_id}/{vacancy_id}")
async def remove_favorite(user_id: int, vacancy_id: str):
    async with async_engine.connect() as conn:
        await conn.execute(
            delete(favorites).where(
                favorites.c.user_id == user_id,
                favorites.c.vacancy_id == vacancy_id
            )
        )
        await conn.commit()
    return {"message": "Removed from favorites"}