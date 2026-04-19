from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from utils.validators import validate_phone_number


class MasterPublicResponse(BaseModel):
    name: str
    slug: str
    timezone: str = "Europe/Moscow"

    model_config = ConfigDict(from_attributes=True)


class SlotResponse(BaseModel):
    datetime_start: datetime
    datetime_end: datetime


class BookingCreate(BaseModel):
    client_name: str
    client_phone: str | None = None
    client_email: str | None = None
    client_social: str | None = None
    service_id: int
    datetime_start: datetime
    notes: str | None = None

    @field_validator("client_phone", mode="before")
    @classmethod
    def validate_phone(cls, v):
        if v is None:
            return v
        return validate_phone_number(v)


class BookingPublicResponse(BaseModel):
    id: int
    client_name: str
    datetime_start: datetime
    datetime_end: datetime
    status: str
    cancel_token: str  # отдаём клиенту чтобы мог отменить запись

    model_config = ConfigDict(from_attributes=True)
