from pydantic import BaseModel, ConfigDict
from datetime import datetime


class BookingResponse(BaseModel):
    id: int
    client_name: str
    client_phone: str | None = None
    client_email: str | None
    client_social: str | None = None

    datetime_start: datetime
    datetime_end: datetime
    status: str
    created_at: datetime
    service_id: int
    service_name: str | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class BookingStatusUpdate(BaseModel):
    status: str  # confirmed / cancelled (Подтверждение / отмена записи)


class BookingNotesUpdate(BaseModel):
    notes: str | None = None
