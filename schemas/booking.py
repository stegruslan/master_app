from pydantic import BaseModel, ConfigDict
from datetime import datetime


class BookingResponse(BaseModel):
    id: int
    client_name: str
    client_phone: str
    client_email: str | None
    datetime_start: datetime
    datetime_end: datetime
    status: str
    created_at: datetime
    service_id: int
    service_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class BookingStatusUpdate(BaseModel):
    status: str  # confirmed / cancelled (Подтверждение / отмена записи)
