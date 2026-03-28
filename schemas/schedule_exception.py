from pydantic import BaseModel, model_validator
from datetime import date, time
from typing import Literal, Optional


class ScheduleExceptionCreate(BaseModel):
    date: date
    type: Literal["dayoff", "block"]
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    @model_validator(mode="after")
    def check_block_times(self):
        if self.type == "block":
            if not self.start_time or not self.end_time:
                raise ValueError("Для перерыва необходимо указать начало и конец")
            if self.start_time >= self.end_time:
                raise ValueError("Время начала должно быть раньше времени окончания")
        return self


class ScheduleExceptionOut(BaseModel):
    id: int
    date: date
    type: str
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    model_config = {"from_attributes": True}
