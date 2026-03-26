from fastapi import APIRouter, HTTPException
from sqlalchemy import select, insert, update, delete
from database import async_engine
from models import profiles, user_skills, work_experience, education, skills
from schemas import ProfileUpdate, ContactsUpdate, BioUpdate, SkillsUpdate, WorkExperienceCreate, EducationCreate

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.post("/{user_id}")
async def create_profile(user_id: int, data: ProfileUpdate):
    values = {k: v for k, v in data.model_dump().items() if v is not None}

    async with async_engine.connect() as conn:
        # ❗ проверка — вдруг уже есть профиль
        existing = await conn.execute(
            select(profiles).where(profiles.c.user_id == user_id)
        )

        if existing.fetchone():
            raise HTTPException(status_code=400, detail="Profile already exists")

        await conn.execute(
            insert(profiles).values(user_id=user_id, **values)
        )
        await conn.commit()

    return {"message": "Profile created"}

@router.put("/{user_id}")
async def update_profile(user_id: int, data: ProfileUpdate):
    values = {k: v for k, v in data.model_dump().items() if v is not None}
    async with async_engine.connect() as conn:
        await conn.execute(
            update(profiles).where(profiles.c.user_id == user_id).values(**values)
        )
        await conn.commit()
    return {"message": "Profile updated"}


@router.put("/{user_id}/contacts")
async def update_contacts(user_id: int, data: ContactsUpdate):
    values = {k: v for k, v in data.model_dump().items() if v is not None}
    async with async_engine.connect() as conn:
        await conn.execute(
            update(profiles).where(profiles.c.user_id == user_id).values(**values)
        )
        await conn.commit()
    return {"message": "Contacts updated"}


@router.put("/{user_id}/bio")
async def update_bio(user_id: int, data: BioUpdate):
    async with async_engine.connect() as conn:
        await conn.execute(
            update(profiles).where(profiles.c.user_id == user_id).values(bio=data.bio)
        )
        await conn.commit()
    return {"message": "Bio updated"}


@router.put("/{user_id}/skills")
async def update_skills(user_id: int, data: SkillsUpdate):
    async with async_engine.connect() as conn:
        # удалить старые навыки
        await conn.execute(
            delete(user_skills).where(user_skills.c.user_id == user_id)
        )
        # добавить новые
        for skill_id in data.skill_ids:
            await conn.execute(
                insert(user_skills).values(user_id=user_id, skill_id=skill_id)
            )
        await conn.commit()
    return {"message": "Skills updated"}


@router.get("/skills")
async def get_all_skills():
    async with async_engine.connect() as conn:
        result = await conn.execute(select(skills))
        return result.mappings().all()


@router.post("/{user_id}/experience")
async def add_experience(user_id: int, data: WorkExperienceCreate):
    async with async_engine.connect() as conn:
        await conn.execute(
            insert(work_experience).values(user_id=user_id, **data.model_dump())
        )
        await conn.commit()
    return {"message": "Experience added"}


@router.delete("/{user_id}/experience/{exp_id}")
async def delete_experience(user_id: int, exp_id: int):
    async with async_engine.connect() as conn:
        await conn.execute(
            delete(work_experience).where(
                work_experience.c.id == exp_id,
                work_experience.c.user_id == user_id
            )
        )
        await conn.commit()
    return {"message": "Experience deleted"}


@router.post("/{user_id}/education")
async def add_education(user_id: int, data: EducationCreate):
    async with async_engine.connect() as conn:
        await conn.execute(
            insert(education).values(user_id=user_id, **data.model_dump())
        )
        await conn.commit()
    return {"message": "Education added"}


@router.delete("/{user_id}/education/{edu_id}")
async def delete_education(user_id: int, edu_id: int):
    async with async_engine.connect() as conn:
        await conn.execute(
            delete(education).where(
                education.c.id == edu_id,
                education.c.user_id == user_id
            )
        )
        await conn.commit()
    return {"message": "Education deleted"}

@router.get("/")
async def get_all_profiles():
    async with async_engine.connect() as conn:
        # Получаем профили с нужными полями
        result = await conn.execute(
            select(
                profiles.c.user_id,
                profiles.c.first_name,
                profiles.c.last_name,
                profiles.c.specialization,
                profiles.c.city,
                profiles.c.level,
                profiles.c.salary_min,
                profiles.c.salary_max,
            )
        )
        profiles_data = result.mappings().all()

        if not profiles_data:
            return []

        # Получаем скиллы всех юзеров одним запросом
        skills_result = await conn.execute(
            select(user_skills.c.user_id, skills.c.name)
            .join(skills, skills.c.id == user_skills.c.skill_id)
        )
        # Группируем скиллы по user_id: {user_id: [skill1, skill2, ...]}
        skills_map = {}
        for row in skills_result.mappings().all():
            skills_map.setdefault(row["user_id"], []).append(row["name"])

    # Собираем итоговый список
    def count_filled(p):
        score = 0
        for field in ["first_name", "last_name", "specialization", "city", "level", "salary_min", "salary_max"]:
            if p[field] is not None and p[field] != "":
                score += 1
        # Скиллы тоже считаем — каждый скилл +1
        if skills_map.get(p["user_id"]):
            score += 1
        return score

    result_list = [
        {
            "user_id": p["user_id"],
            "first_name": p["first_name"],
            "last_name": p["last_name"],
            "specialization": p["specialization"],
            "city": p["city"],
            "level": p["level"],
            "salary_min": p["salary_min"],
            "salary_max": p["salary_max"],
            "skills": skills_map.get(p["user_id"], []),
        }
        for p in profiles_data
    ]

    result_list.sort(key=count_filled, reverse=True)

    return result_list

@router.get("/{user_id}")
async def get_profile(user_id: int):
    async with async_engine.connect() as conn:
        # основные данные профиля
        profile = await conn.execute(
            select(profiles).where(profiles.c.user_id == user_id)
        )
        profile_data = profile.mappings().fetchone()

        if not profile_data:
            raise HTTPException(status_code=404, detail="Profile not found")

        # скиллы
        skills_result = await conn.execute(
            select(skills).join(user_skills, skills.c.id == user_skills.c.skill_id)
            .where(user_skills.c.user_id == user_id)
        )
        skills_data = skills_result.mappings().all()

        # опыт работы
        exp_result = await conn.execute(
            select(work_experience).where(work_experience.c.user_id == user_id)
        )
        exp_data = exp_result.mappings().all()

        # образование
        edu_result = await conn.execute(
            select(education).where(education.c.user_id == user_id)
        )
        edu_data = edu_result.mappings().all()

    return {
        "profile": profile_data,
        "skills": skills_data,
        "experience": exp_data,
        "education": edu_data,
    }

@router.delete("/{user_id}")
async def delete_profile(user_id: int):
    async with async_engine.connect() as conn:
        # удаляем зависимости
        await conn.execute(delete(user_skills).where(user_skills.c.user_id == user_id))
        await conn.execute(delete(work_experience).where(work_experience.c.user_id == user_id))
        await conn.execute(delete(education).where(education.c.user_id == user_id))

        # удаляем сам профиль
        await conn.execute(delete(profiles).where(profiles.c.user_id == user_id))

        await conn.commit()

    return {"message": "Profile deleted"}