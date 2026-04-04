from pydantic import BaseModel, ConfigDict


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
    timezone: str | None = None
