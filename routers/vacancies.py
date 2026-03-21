from fastapi import APIRouter, Query
from sqlalchemy import select, and_
from database import async_engine
from models import vacancies
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import ARRAY, TEXT

router = APIRouter(
    prefix="/vacancies",
    tags=["vacancies"]
)


# Get all vacancies
@router.get("/")
async def get_all_vacancies():
    async with async_engine.connect() as conn:
        result = await conn.execute(select(vacancies))
        return result.mappings().all()


# Get vacancies by salary range
@router.get("/salary")
async def get_by_salary(
    min_salary: Optional[int] = None,
    max_salary: Optional[int] = None
):
    async with async_engine.connect() as conn:
        conditions = []
        if min_salary is not None:
            conditions.append(vacancies.c.salary_min >= min_salary)
            conditions.append(vacancies.c.salary_min.isnot(None))
        if max_salary is not None:
            conditions.append(vacancies.c.salary_max <= max_salary)
            conditions.append(vacancies.c.salary_max.isnot(None))

        if conditions:
            result = await conn.execute(
                select(vacancies).where(and_(*conditions))
            )
        else:
            result = await conn.execute(select(vacancies))

        return result.mappings().all()


# Get vacancies created this week
@router.get("/this-week")
async def get_this_week():
    week_ago = datetime.utcnow() - timedelta(days=7)
    async with async_engine.connect() as conn:
        result = await conn.execute(
            select(vacancies).where(vacancies.c.created_at >= week_ago)
        )
        return result.mappings().all()


# Search by title + optional tags filter
@router.get("/search")
async def search_vacancies(
    query: Optional[str] = None,
    tags: Optional[list[str]] = Query(default=None)
):
    async with async_engine.connect() as conn:
        conditions = []

        if query:
            conditions.append(
                vacancies.c.position_name.ilike(f"%{query}%")
            )

        if tags:
            for tag in tags:
                conditions.append(
                    vacancies.c.tags.contains(cast([tag], ARRAY(TEXT)))
        )

        if conditions:
            result = await conn.execute(
                select(vacancies).where(and_(*conditions))
            )
        else:
            result = await conn.execute(select(vacancies))

        return result.mappings().all()


# Get vacancy by id
@router.get("/{vacancy_id}")
async def get_vacancy(vacancy_id: str):
    async with async_engine.connect() as conn:
        result = await conn.execute(
            select(vacancies).where(vacancies.c.id == vacancy_id)
        )
        return result.mappings().fetchone()