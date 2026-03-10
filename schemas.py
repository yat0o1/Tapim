from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Literal


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    confirm_password: str
    role: Literal["recruiter", "applicant"] = "applicant"

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


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str