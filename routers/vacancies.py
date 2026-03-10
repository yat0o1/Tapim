from fastapi import APIRouter, Query
from sqlalchemy import select
from database import async_engine
from models import vacancies
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/vacancies", 
    tags=["vacancies"]
    )


# Get all vacancies
@router.get("/")
async def get_all_vacancies():
    async with async_engine.connect() as conn:  # opens a connection to DB, closes automatically when done
        result = await conn.execute(select(vacancies))  # SELECT * FROM vacancies
        return result.mappings().all()  
        # .mappings() → converts rows to dict-like objects {column: value}
        # .all() → fetches all rows at once


# Get vacancies with salary greater than N
@router.get("/salary")
async def get_by_salary(min_salary: int = 0):
    # Query(...) → means this parameter is REQUIRED in the URL, e.g. /vacancies/salary?min_salary=50000
    # if you use Query(0) instead of Query(...) it becomes optional with default value 0
    async with async_engine.connect() as conn:
        result = await conn.execute(
            select(vacancies).where(vacancies.c.salary > min_salary,
                                    vacancies.c.salary.isnot(None)
                                    )
            # .where() → adds WHERE clause, same as SQL: WHERE salary > min_salary
        )
        return result.mappings().all()


# Get vacancies created this week
@router.get("/this-week")
async def get_this_week():
    week_ago = datetime.utcnow() - timedelta(days=7)  
    # datetime.utcnow() → current time in UTC
    # timedelta(days=7) → represents 7 days duration, subtracting gives us date 7 days ago
    async with async_engine.connect() as conn:
        result = await conn.execute(
            select(vacancies).where(vacancies.c.created_at >= week_ago)
            # >= week_ago → only rows created after that date
        )
        return result.mappings().all()


@router.get("/search")
async def search_vacancies(query: str = None):
    async with async_engine.connect() as conn:
        if query is None:
            # no query → return all vacancies
            result = await conn.execute(select(vacancies))
        else:
            # search by title, case-insensitive
            result = await conn.execute(
                select(vacancies).where(
                    vacancies.c.title.ilike(f"%{query}%")
                )
            )
        return result.mappings().all()

# Get vacancy by id
@router.get("/{vacancy_id}")
async def get_vacancy(vacancy_id: int):
    # {vacancy_id} → dynamic URL parameter, e.g. /vacancies/3 → vacancy_id = 3
    async with async_engine.connect() as conn:
        result = await conn.execute(
            select(vacancies).where(vacancies.c.id == vacancy_id)
        )
        return result.mappings().fetchone()  
        # .fetchone() → fetches only ONE row instead of all, since we expect a single vacancy by id
