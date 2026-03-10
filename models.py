from sqlalchemy import Table, Column, Integer, String, Text, TIMESTAMP, ForeignKey, MetaData
from sqlalchemy.sql import func

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

profiles = Table(
    "profiles",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("first_name", String(100)),
    Column("last_name", String(100)),
    Column("bio", Text),
    Column("resume_url", Text),
)

vacancies = Table(
    "vacancies",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("title", String(255), nullable=False),
    Column("description", Text),
    Column("salary", Integer),
    Column("created_by", Integer, ForeignKey("users.id")),
    Column("created_at", TIMESTAMP, server_default=func.now()),
)

applications = Table(
    "applications",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("vacancy_id", Integer, ForeignKey("vacancies.id")),
    Column("status", String(50), server_default="pending"),
    Column("created_at", TIMESTAMP, server_default=func.now()),
)