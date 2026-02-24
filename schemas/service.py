from pydantic import BaseModel, ConfigDict


class ServiceCreate(BaseModel):
    name: str
    duration: int
    price: int


class ServiceUpdate(BaseModel):
    name: str | None = None
    duration: int | None = None
    price: int | None = None
    is_active: bool | None = None


class ServiceResponse(BaseModel):
    id: int
    name: str
    duration: int
    price: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
