from pydantic import BaseModel, field_validator, EmailStr
from utils.validators import validate_phone_number, validate_password


class MasterRegister(BaseModel):
    name: str
    phone: str
    password: str
    email: EmailStr

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        return validate_phone_number(v)

    @field_validator("password")
    @classmethod
    def check_password(cls, v):
        return validate_password(v)


class MasterLogin(BaseModel):
    phone: str
    password: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        return validate_phone_number(v)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def check_password(cls, v):
        return validate_password(v)
