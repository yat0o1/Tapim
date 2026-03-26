from typing import Literal, Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from email_validator import validate_email, EmailNotValidError
from datetime import datetime, date
from typing import List, Optional
import uuid


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    
class ApplicantRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    confirm_password: str
    first_name: str = Field(..., max_length=100)
    city: str = Field(..., max_length=100)

    @field_validator("email")
    @classmethod
    def validate_email_domain(cls, email):
        try:
            validate_email(email, check_deliverability=True)
        except EmailNotValidError:
            raise ValueError("Email domain does not exist")
        return email

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

class RecruiterRegisterStep1(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    confirm_password: str
    first_name: str = Field(..., max_length=100)

    @field_validator("email")
    @classmethod
    def validate_email_domain(cls, email):
        try:
            validate_email(email, check_deliverability=True)
        except EmailNotValidError:
            raise ValueError("Email domain does not exist")
        return email

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

class RecruiterRegisterStep2(BaseModel):
    user_id: int
    company_name: str = Field(..., max_length=255)
    company_size: Literal["small", "medium", "big"]
    company_site: Optional[str] = None
    user_role_in_company: str = Field(..., max_length=100)

# ─── PROFILE

class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    specialization: Optional[str] = None
    city: Optional[str] = None
    work_format: Optional[Literal["remote", "hybrid", "fulltime"]] = None
    level: Optional[Literal["junior", "middle", "senior"]] = None

class ContactsUpdate(BaseModel):
    phone: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None

class BioUpdate(BaseModel):
    bio: str

class SkillsUpdate(BaseModel):
    skill_ids: List[int]  # список id навыков

class WorkExperienceCreate(BaseModel):
    position: str
    company_name: str
    start_date: date
    end_date: Optional[date] = None
    description: Optional[str] = None


class EducationCreate(BaseModel):
    specialization: str
    university: str
    start_date: date
    end_date: Optional[date] = None

# ─── EMAIL verification

class VerifyEmail(BaseModel):
    user_id: int
    code: str = Field(..., min_length=6, max_length=6)

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    user_id: int
    code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=6, max_length=72)
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self
    
class VacancyCreate(BaseModel):
    company_name: str
    location: Optional[str] = None
    specialization: Optional[str] = None
    position_name: str
    vacancy_description: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    salary_type: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_social: Optional[str] = None
