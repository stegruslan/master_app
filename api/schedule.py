from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.dependencies import get_current_master
from core.logging import get_logger
from models.user import Master
from models.schedule import WorkSchedule
from schemas.schedule import ScheduleUpdate, ScheduleResponce
from datetime import time

router = APIRouter(prefix="/schedule", tags=["schedule"])
logger = get_logger(__name__)

WEEKDAYS = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье",
}


@router.get("/", response_model=list[ScheduleResponce])
async def get_schedule(
    master: Master = Depends(get_current_master), db: AsyncSession = Depends(get_db)
):
    """Получить расписание мастера на все дни недели."""
    result = await db.execute(
        select(WorkSchedule)
        .where(WorkSchedule.master_id == master.id)
        .order_by(WorkSchedule.weekday)
    )

    return result.scalars().all()


@router.put("/{weekday}", response_model=ScheduleResponce)
async def update_schedule(
    weekday: int,
    data: ScheduleUpdate,
    master: Master = Depends(get_current_master),
    db: AsyncSession = Depends(get_db),
):
    """Обновить расписание на конкретный день недели (0=Пн, 6=Вс)."""

    if weekday not in WEEKDAYS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный день недели. Используй 0-6",
        )
    result = await db.execute(
        select(WorkSchedule).where(
            WorkSchedule.master_id == master.id, WorkSchedule.weekday == weekday
        )
    )

    schedule = result.scalar_one_or_none()

    if schedule is None:
        schedule = WorkSchedule(
            master_id=master.id,
            weekday=weekday,
            start_time=time.fromisoformat(data.start_time),
            end_time=time.fromisoformat(data.end_time),
            is_working=data.is_working,
        )

        db.add(schedule)

    else:
        schedule.start_time = time.fromisoformat(data.start_time)
        schedule.end_time = time.fromisoformat(data.end_time)
        schedule.is_working = data.is_working

    await db.commit()
    await db.refresh(schedule)

    logger.info(
        f"Мастер {master.phone} обновил расписание: "
        f"{WEEKDAYS[weekday]} {data.start_time}-{data.end_time}"
    )

    return schedule
