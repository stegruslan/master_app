from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.dependencies import get_current_master
from core.logging import get_logger
from models.user import Master
from models.schedule import WorkSchedule
from models.schedule_exception import ScheduleException
from schemas.schedule import ScheduleUpdate, ScheduleResponce
from schemas.schedule_exception import ScheduleExceptionCreate, ScheduleExceptionOut
from datetime import time, date

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


@router.get("/exceptions", response_model=list[ScheduleExceptionOut])
async def get_exceptions(
    master: Master = Depends(get_current_master), db: AsyncSession = Depends(get_db)
):
    """Получить все исключения в расписании мастера."""

    result = await db.execute(
        select(ScheduleException)
        .where(ScheduleException.master_id == master.id)
        .order_by(ScheduleException.date)
    )
    return result.scalars().all()


@router.post("/exceptions/toggle", response_model=ScheduleExceptionOut)
async def toggle_dayoff(
    data: ScheduleExceptionCreate,
    master: Master = Depends(get_current_master),
    db: AsyncSession = Depends(get_db),
):
    """Переключить выходной день — если есть удалить, если нет создать."""

    if data.type != "dayoff":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот эндпоинт только для выходных дней",
        )

    result = await db.execute(
        select(ScheduleException).where(
            ScheduleException.master_id == master.id,
            ScheduleException.date == data.date,
            ScheduleException.type == "dayoff",
        )
    )
    exc = result.scalar_one_or_none()

    if exc:
        exc_data = ScheduleExceptionOut.model_validate(exc)
        await db.delete(exc)
        await db.commit()
        logger.info(f"Мастер {master.phone} снял выходной: {data.date}")
        return exc_data

    new_exc = ScheduleException(master_id=master.id, date=data.date, type="dayoff")
    db.add(new_exc)
    await db.commit()
    await db.refresh(new_exc)
    logger.info(f"Мастер {master.phone} поставил выходной: {data.date}")
    return new_exc


@router.delete("/exceptions/{exception_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exception(
    exception_id: int,
    master: Master = Depends(get_current_master),
    db: AsyncSession = Depends(get_db),
):
    """Удалить конкретное исключение по id (для перерывов)."""
    result = await db.execute(
        select(ScheduleException).where(
            ScheduleException.id == exception_id,
            ScheduleException.master_id == master.id,
        )
    )
    exc = result.scalar_one_or_none()

    if not exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Исключение не найдено"
        )
    await db.delete(exc)
    await db.commit()
    logger.info(f"Мастер {master.phone} удалил исключение id={exception_id}")


@router.post("/exceptions", response_model=ScheduleExceptionOut)
async def create_exception(
    data: ScheduleExceptionCreate,
    master: Master = Depends(get_current_master),
    db: AsyncSession = Depends(get_db),
):
    """Создать исключение (перерыв type=block)."""
    new_exc = ScheduleException(
        master_id=master.id,
        date=data.date,
        type=data.type,
        start_time=data.start_time,
        end_time=data.end_time,
    )
    db.add(new_exc)
    await db.commit()
    await db.refresh(new_exc)
    logger.info(f"Мастер {master.phone} добавил исключение {data.type} на {data.date}")
    return new_exc
