from sqlalchemy import Table, Column, Integer, String, Text, TIMESTAMP, Boolean, ForeignKey, MetaData , BOOLEAN
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from sqlalchemy import Date


metadata_obj = MetaData()

roles = Table(
    "roles",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(50), nullable=False),
)

users = Table(
    "users",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("email", String(255), nullable=False),
    Column("password_hash", Text, nullable=False),
    Column("role_id", Integer, ForeignKey("roles.id")),
    Column("created_at", TIMESTAMP, server_default=func.now()),
)

vacancies = Table(
    "vacancies",
    metadata_obj,
    Column("id", UUID, primary_key=True),
    Column("source_id", Integer),
    Column("created_at", TIMESTAMP, server_default=func.now()),
    Column("source_type", String(50)),
    Column("company_name", String(255)),
    Column("location", String(255)),
    Column("specialization", String(255)),
    Column("position_name", String(500)),
    Column("vacancy_description", Text),
    Column("salary_min", Integer),
    Column("salary_max", Integer),
    Column("salary_currency", String(10)),
    Column("salary_type", String(10)),
    Column("contact_name", String(255)),
    Column("contact_phone", String(100)),
    Column("contact_social", String(500)),
    Column("tags", ARRAY(String)),
    Column("created_by", Integer, ForeignKey("users.id"), nullable=True),
    Column("skills", ARRAY(String)),
)

applications = Table(
    "applications",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("vacancy_id", UUID, ForeignKey("vacancies.id")),
    Column("status", String(50), server_default="pending"),
    Column("created_at", TIMESTAMP, server_default=func.now()),
)

messages = Table(
    "messages",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sender_id", Integer, ForeignKey("users.id")),
    Column("receiver_id", Integer, ForeignKey("users.id")),
    Column("content", Text, nullable=False),
    Column("created_at", TIMESTAMP, server_default=func.now()),
    Column("is_read", Boolean, server_default="false"),
)

profiles = Table(
    "profiles",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("first_name", String(100)),
    Column("last_name", String(100)),
    Column("city", String(100)),
    Column("phone", String(50)),
    Column("specialization", String(255)),  # "Frontend Dev" etc
    Column("level", String(50)),            # junior, middle, senior
    Column("work_format", String(50)),      # remote, hybrid, fulltime
    Column("bio", Text),
    Column("github_url", String(255)),
    Column("linkedin_url", String(255)),
    Column("resume_url", Text),
    Column("salary_min", Integer, nullable=True),
    Column("salary_max", Integer, nullable=True),
)

# Для рекрутеров
companies = Table(
    "companies",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("company_name", String(255)),
    Column("company_size", String(50)),
    Column("company_site", String(255)),
    Column("user_role_in_company", String(100)),
    Column("city", String(100)),
    Column("industry", String(100)),
    Column("about", Text),
    Column("linkedin", String(255)),
    Column("phone", String(50)),
    Column("email", String(255)),
    Column("stack", ARRAY(String)),
)

skills = Table(
    "skills",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100), nullable=False),  # React, Python etc
)

user_skills = Table(
    "user_skills",
    metadata_obj,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("skill_id", Integer, ForeignKey("skills.id")),
)

work_experience = Table(
    "work_experience",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("position", String(255)),
    Column("company_name", String(255)),
    Column("start_date", Date),
    Column("end_date", Date, nullable=True),
    Column("description", Text),
)

education = Table(
    "education",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("specialization", String(255)),
    Column("university", String(255)),
    Column("start_date", Date),
    Column("end_date", Date, nullable=True),
)

# Верификация email
email_verifications = Table(
    "email_verifications",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("code", String(6), nullable=False),
    Column("created_at", TIMESTAMP, server_default=func.now()),
    Column("expires_at", TIMESTAMP, nullable=False),
    Column("is_used", Boolean, server_default="false"),
)

favorites = Table(
    "favorites",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("vacancy_id", UUID, ForeignKey("vacancies.id")),
    Column("created_at", TIMESTAMP, server_default=func.now()),
)