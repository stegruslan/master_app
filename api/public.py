from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.logging import get_logger
from models.user import Master
from models.service import Service
from models.schedule import WorkSchedule
from models.booking import Booking
from models.schedule_exception import ScheduleException
from schemas.public import (
    MasterPublicResponse,
    SlotResponse,
    BookingCreate,
    BookingPublicResponse,
)
from schemas.service import ServiceResponse
from utils.telegram import send_telegram_message
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import uuid

router = APIRouter(tags=["public"])
logger = get_logger(__name__)


@router.get("/book/{slug}", response_model=MasterPublicResponse)
async def get_master_page(slug: str, db: AsyncSession = Depends(get_db)):
    """Публичная страница мастера — имя и список активных услуг."""

    result = await db.execute(
        select(Master).where(Master.slug == slug, Master.is_active.is_(True))
    )

    master = result.scalar_one_or_none()

    if master is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Мастер не найден"
        )

    return master


@router.get("/book/{slug}/services", response_model=list[ServiceResponse])
async def get_master_services(slug: str, db: AsyncSession = Depends(get_db)):
    """Получить список активных услуг мастера."""

    result = await db.execute(
        select(Master).where(Master.slug == slug, Master.is_active.is_(True))
    )

    master = result.scalar_one_or_none()

    if master is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Мастер не найден"
        )

    result = await db.execute(
        select(Service).where(
            Service.master_id == master.id, Service.is_active.is_(True)
        )
    )

    return result.scalars().all()


@router.get("/book/{slug}/slots", response_model=list[SlotResponse])
async def get_slots(
    slug: str, service_id: int, date: str, db: AsyncSession = Depends(get_db)
):
    """Получить свободные слоты для записи на конкретную дату."""

    result = await db.execute(
        select(Master).where(Master.slug == slug, Master.is_active.is_(True))
    )

    master = result.scalar_one_or_none()

    if master is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Мастер не найден"
        )

    result = await db.execute(
        select(Service).where(
            Service.id == service_id,
            Service.master_id == master.id,
            Service.is_active.is_(True),
        )
    )

    service = result.scalar_one_or_none()

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Услуга не найдена"
        )

    target_date = datetime.strptime(date, "%Y-%m-%d")
    weekday = target_date.weekday()

    # получаем расписание мастера на этот день
    result = await db.execute(
        select(WorkSchedule).where(
            WorkSchedule.master_id == master.id, WorkSchedule.weekday == weekday
        )
    )

    schedule = result.scalar_one_or_none()

    # мастер не работает в этот день
    if schedule is None or not schedule.is_working:
        return []

    # проверка  исключения на конкретную дату
    target_date_only = target_date.date()
    exc_result = await db.execute(
        select(ScheduleException).where(
            ScheduleException.master_id == master.id,
            ScheduleException.date == target_date_only,
        )
    )
    exceptions = exc_result.scalars().all()

    # если весь день выходной — возвращаем пустой список

    if any(e.type == "dayoff" for e in exceptions):
        return []

    # собираем заблокированные промежутки (перерывы)
    blocked_ranges = [
        (e.start_time, e.end_time)
        for e in exceptions
        if e.type == "block" and e.start_time and e.end_time
    ]

    # генерируем все слоты на день
    slots = []
    master_tz = ZoneInfo(master.timezone or "Europe/Moscow")
    current = (
        datetime.combine(target_date.date(), schedule.start_time)
        .replace(tzinfo=master_tz)
        .astimezone(timezone.utc)
    )
    end_of_day = (
        datetime.combine(target_date.date(), schedule.end_time)
        .replace(tzinfo=master_tz)
        .astimezone(timezone.utc)
    )
    duration = timedelta(minutes=service.duration)

    step = timedelta(minutes=10)
    while current + duration <= end_of_day:
        slots.append((current, current + duration))
        current += step

    # получаем уже занятые записи на этот день
    day_start = (
        datetime.combine(target_date.date(), schedule.start_time)
        .replace(tzinfo=master_tz)
        .astimezone(timezone.utc)
    )
    day_end = (
        datetime.combine(target_date.date(), schedule.end_time)
        .replace(tzinfo=master_tz)
        .astimezone(timezone.utc)
    )

    result = await db.execute(
        select(Booking).where(
            Booking.master_id == master.id,
            Booking.datetime_start >= day_start,
            Booking.datetime_end <= day_end,
            Booking.status != "cancelled",
        )
    )

    existing_bookings = result.scalars().all()

    # фильтруем занятые слоты

    free_slots = []

    for slot_start, slot_end in slots:
        is_busy = False
        for booking in existing_bookings:
            booking_start = booking.datetime_start
            booking_end = booking.datetime_end

            if booking_start.tzinfo is None:
                booking_start = booking_start.replace(tzinfo=timezone.utc)
            if booking_end.tzinfo is None:
                booking_end = booking_end.replace(tzinfo=timezone.utc)

            if slot_start < booking_end and slot_end > booking_start:
                is_busy = True
                break
        # проверяем перерывы
        if not is_busy and blocked_ranges:
            slot_start_local = slot_start.astimezone(master_tz).time()
            slot_end_local = slot_end.astimezone(master_tz).time()

            for block_start, block_end in blocked_ranges:
                if slot_start_local < block_end and slot_end_local > block_start:
                    is_busy = True
                    break
        if not is_busy:
            free_slots.append(
                SlotResponse(datetime_start=slot_start, datetime_end=slot_end)
            )
    return free_slots


@router.post("/book/{slug}", response_model=BookingPublicResponse)
async def create_booking(
    slug: str, data: BookingCreate, db: AsyncSession = Depends(get_db)
):
    """Клиент записывается к мастеру."""

    result = await db.execute(
        select(Master).where(Master.slug == slug, Master.is_active.is_(True))
    )

    master = result.scalar_one_or_none()

    if master is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Мастер не найден"
        )
    result = await db.execute(
        select(Service).where(
            Service.id == data.service_id,
            Service.master_id == master.id,
            Service.is_active.is_(True),
        )
    )

    service = result.scalar_one_or_none()

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Услуга не найдена"
        )

    weekday = data.datetime_start.weekday()
    result = await db.execute(
        select(WorkSchedule).where(
            WorkSchedule.master_id == master.id, WorkSchedule.weekday == weekday
        )
    )

    schedule = result.scalar_one_or_none()

    if schedule is None or not schedule.is_working:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Мастер не работает в этот день",
        )
    master_tz = ZoneInfo(master.timezone or "Europe/Moscow")

    local_dt = data.datetime_start.astimezone(master_tz)

    start_time = local_dt.time()
    if start_time < schedule.start_time or start_time >= schedule.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Мастер не работает в это время",
        )

    datetime_end = data.datetime_start + timedelta(minutes=service.duration)

    # проверяем что слот свободен
    result = await db.execute(
        select(Booking).where(
            Booking.master_id == master.id,
            Booking.status != "cancelled",
            Booking.datetime_start < datetime_end,
            Booking.datetime_end > data.datetime_start,
        )
    )

    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Это время уже занято"
        )

    booking = Booking(
        master_id=master.id,
        service_id=service.id,
        client_name=data.client_name,
        client_phone=data.client_phone,
        client_email=data.client_email,
        datetime_start=data.datetime_start,
        datetime_end=datetime_end,
        cancel_token=str(uuid.uuid4()),
        notes=data.notes,
    )

    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    if master.telegram_id:
        local_start = booking.datetime_start.astimezone(master_tz)
        await send_telegram_message(
            master.telegram_id,
            f"📅 <b>Новая запись!</b>\n\n"
            f"👤 {booking.client_name}\n"
            f"📞 {booking.client_phone}\n"
            f"💼 {service.name}\n"
            f"🕐 {local_start.strftime('%d.%m.%Y %H:%M')}",
        )

    logger.info(
        f"Новая запись к мастеру {master.phone}: "
        f"клиент {data.client_name} на {data.datetime_start}"
    )

    return booking


@router.get("/cancel/{cancel_token}")
async def cancel_booking(cancel_token: str, db: AsyncSession = Depends(get_db)):
    """Клиент отменяет запись по токену."""

    result = await db.execute(
        select(Booking).where(Booking.cancel_token == cancel_token)
    )

    booking = result.scalar_one_or_none()

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Запись не найдена"
        )
    if booking.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Запись уже отменена"
        )
    booking.status = "cancelled"
    await db.commit()

    logger.info(f"Клиент отменил запись {booking.id}")

    return {"detail": "Запись отменена"}
