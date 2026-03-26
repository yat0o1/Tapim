from fastapi import APIRouter, HTTPException
from sqlalchemy import select, insert, delete
from database import async_engine
from models import favorite_worksheets, profiles

router = APIRouter(prefix="/favorite-profiles", tags=["favorite profiles"])

@router.post("/{user_id}/{profile_id}")
async def add_favorite_profile(user_id: int, profile_id: int):
    async with async_engine.connect() as conn:

        # проверка существования
        existing = await conn.execute(
            select(favorite_worksheets).where(
                favorite_worksheets.c.user_id == user_id,
                favorite_worksheets.c.profile_id == profile_id
            )
        )

        if existing.fetchone():
            raise HTTPException(status_code=400, detail="Already in favorites")

        await conn.execute(
            insert(favorite_worksheets).values(
                user_id=user_id,
                profile_id=profile_id
            )
        )

        await conn.commit()

    return {"message": "Added to favorites"}

@router.get("/{user_id}")
async def get_favorite_profiles(user_id: int):
    async with async_engine.connect() as conn:
        result = await conn.execute(
            select(profiles)
            .join(
                favorite_worksheets,
                profiles.c.id == favorite_worksheets.c.profile_id
            )
            .where(favorite_worksheets.c.user_id == user_id)
        )

        return result.mappings().all()
    
@router.delete("/{user_id}/{profile_id}")
async def remove_favorite_profile(user_id: int, profile_id: int):
    async with async_engine.connect() as conn:
        await conn.execute(
            delete(favorite_worksheets).where(
                favorite_worksheets.c.user_id == user_id,
                favorite_worksheets.c.profile_id == profile_id
            )
        )

        await conn.commit()

    return {"message": "Removed from favorites"}