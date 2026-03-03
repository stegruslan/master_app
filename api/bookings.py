from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from core.database import get_db
from core.dependencies import get_current_master
from core.logging import get_logger
from models.user import Master
from models.booking import Booking
from models.service import Service
from schemas.booking import BookingResponse, BookingStatusUpdate

router = APIRouter(prefix="/bookings", tags=["bookings"])
logger = get_logger(__name__)


@router.get("/", response_model=list[BookingResponse])
async def get_bookings(
    master: Master = Depends(get_current_master), db: AsyncSession = Depends(get_db)
):
    """Получить все записи мастера."""

    result = await db.execute(
        select(Booking)
        .options(joinedload(Booking.service))
        .where(Booking.master_id == master.id)
        .order_by(Booking.datetime_start)
    )

    bookings = result.unique().scalars().all()

    response = []
    for b in bookings:
        item = BookingResponse.model_validate(b)
        item.service_name = b.service.name if b.service else None
        response.append(item)

    return response


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    master: Master = Depends(get_current_master),
    db: AsyncSession = Depends(get_db),
):
    """Получить конкретную запись по ID."""

    result = await db.execute(
        select(Booking).where(Booking.id == booking_id, Booking.master_id == master.id)
    )
    booking = result.scalar_one_or_none()

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Запись не найдена"
        )

    return booking


@router.patch("/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
    booking_id: int,
    data: BookingStatusUpdate,
    master: Master = Depends(get_current_master),
    db: AsyncSession = Depends(get_db),
):
    """Обновить статус записи (confirmed / cancelled)."""

    if data.status not in ["confirmed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Статус может быть только confirmed или cancelled",
        )

    result = await db.execute(
        select(Booking).where(Booking.id == booking_id, Booking.master_id == master.id)
    )

    booking = result.scalar_one_or_none()

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Запись не найдена"
        )
    booking.status = data.status
    await db.commit()
    await db.refresh(booking)

    logger.info(
        f"Мастер {master.phone} изменил статус записи {booking_id} на {data.status}"
    )

    return booking
