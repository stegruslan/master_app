from pydantic import BaseModel, ConfigDict
from datetime import time


class ScheduleUpdate(BaseModel):
    start_time: str
    end_time: str
    is_working: bool


class ScheduleResponce(BaseModel):
    id: int
    weekday: int
    start_time: time
    end_time: time
    is_working: bool

    model_config = ConfigDict(from_attributes=True)
