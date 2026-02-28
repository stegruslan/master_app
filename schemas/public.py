from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from utils.validators import validate_phone_number


class MasterPublicResponse(BaseModel):
    name: str
    slug: str

    model_config = ConfigDict(from_attributes=True)


class SlotResponse(BaseModel):
    datetime_start: datetime
    datetime_end: datetime


class BookingCreate(BaseModel):
    client_name: str
    client_phone: str
    client_email: str | None = None
    service_id: int
    datetime_start: datetime

    @field_validator("client_phone")
    @classmethod
    def validate_phone(cls, v):
        return validate_phone_number(v)


class BookingPublicResponse(BaseModel):
    id: int
    client_name: str
    datetime_start: datetime
    datetime_end: datetime
    status: str
    cancel_token: str  # отдаём клиенту чтобы мог отменить запись

    model_config = ConfigDict(from_attributes=True)
