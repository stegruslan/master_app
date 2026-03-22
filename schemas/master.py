from pydantic import BaseModel, ConfigDict, field_validator
from utils.validators import validate_phone_number


class MasterResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: str | None
    slug: str
    is_active: bool
    timezone: str = "Europe/Moscow"

    model_config = ConfigDict(from_attributes=True)


class MasterUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    timezone: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is None:
            return v
        return validate_phone_number(v)
