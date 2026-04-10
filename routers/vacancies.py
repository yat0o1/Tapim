import uuid
from fastapi import APIRouter, Query
from sqlalchemy import select, and_ , cast, delete , case , or_
from database import async_engine
from models import vacancies , profiles
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.dialects.postgresql import ARRAY, TEXT, insert
from schemas import VacancyCreate

router = APIRouter(
    prefix="/vacancies",
    tags=["vacancies"]
)


# Get all vacancies
@router.get("/")
async def get_all_vacancies(user_id: Optional[int] = None):
    async with async_engine.connect() as conn:
        
        user_spec = None
        if user_id:
            profile_result = await conn.execute(
                select(profiles.c.specialization).where(profiles.c.user_id == user_id)
            )
            row = profile_result.fetchone()
            if row:
                user_spec = row[0]

        if user_spec:
            priority = case(
                (vacancies.c.specialization == user_spec, 0),
                else_=1
            )
            stmt = select(vacancies).order_by(priority, vacancies.c.created_at.desc())
        else:
            stmt = select(vacancies).order_by(vacancies.c.created_at.desc())

        result = await conn.execute(stmt)
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

@router.get("/search")
async def search_vacancies(
    query: Optional[str] = None,
    tags: Optional[list[str]] = Query(default=None),
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
):
    async with async_engine.connect() as conn:
        conditions = []

        if query:
            conditions.append(vacancies.c.position_name.ilike(f"%{query}%"))

        if tags:
            for tag in tags:
                conditions.append(
                    vacancies.c.tags.contains(cast([tag.lower()], ARRAY(TEXT)))
                )

        if salary_min is not None:
            conditions.append(vacancies.c.salary_min >= salary_min)

        if salary_max is not None:
            conditions.append(
                or_(
                    vacancies.c.salary_max <= salary_max,
                    vacancies.c.salary_max.is_(None)
                )
            )

        stmt = select(vacancies).where(and_(*conditions)) if conditions else select(vacancies)
        result = await conn.execute(stmt)
        return result.mappings().all()


@router.post("/")
async def create_vacancy(data: VacancyCreate):
    tags = []

    # Навыки
    if data.skills:
        tags.extend(data.skills)

    # Уровень
    if data.level:
        tags.append(data.level)  # "junior" / "intern" / "middle" / "senior" / "lead"

    # Город
    if data.location:
        tags.append(data.location)

    # Специализация
    if data.specialization:
        tags.append(data.specialization)

    # Формат работы
    if data.work_format:
        tags.append(data.work_format)  # "remote" / "office" / "hybrid"

    # Вид занятости
    if data.employment_type:
        tags.append(data.employment_type)  # "full" / "part" / "internship"

    # Зарплата
    if data.salary_min is not None or data.salary_max is not None:
        tags.append("зарплата указана")
    else:
        tags.append("зарплата не указана")

    payload = data.model_dump(exclude={"id", "tags", "source_type", "skills", "level", "work_format", "employment_type"})
    payload.update({
        "id": str(uuid.uuid4()),
        "source_type": "manual",
        "tags": tags if tags else None,
    })

    async with async_engine.connect() as conn:
        await conn.execute(insert(vacancies).values(**payload))
        await conn.commit()

    return {"message": "Vacancy created successfully"}


@router.get("/my/{user_id}")
async def get_my_vacancies(user_id: int):
    async with async_engine.connect() as conn:
        result = await conn.execute(
            select(vacancies).where(vacancies.c.created_by == user_id)
        )
        return result.mappings().all()


@router.delete("/{vacancy_id}")
async def delete_vacancy(vacancy_id: str):
    async with async_engine.connect() as conn:
        await conn.execute(
            delete(vacancies).where(vacancies.c.id == vacancy_id)
        )
        await conn.commit()
    return {"message": "Vacancy deleted"}


# Get vacancy by id
@router.get("/{vacancy_id}")
async def get_vacancy(vacancy_id: str):
    async with async_engine.connect() as conn:
        result = await conn.execute(
            select(vacancies).where(vacancies.c.id == vacancy_id)
        )
        return result.mappings().fetchone()