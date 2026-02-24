from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.dependencies import get_current_master
from core.logging import get_logger
from models.user import Master
from models.service import Service
from schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse

router = APIRouter(prefix="/services", tags=["services"])
logger = get_logger(__name__)


@router.get("/", response_model=list[ServiceResponse])
async def get_services(
    master: Master = Depends(get_current_master), db: AsyncSession = Depends(get_db)
):
    """
    Получить список всех активных услуг текущего мастера.
    """
    result = await db.execute(
        select(Service).where(Service.master_id == master.id, Service.is_active == True)
    )  # noqa: E712

    return result.scalars().all()


@router.post("/", response_model=ServiceResponse)
async def create_service(
    data: ServiceCreate,
    master: Master = Depends(get_current_master),
    db: AsyncSession = Depends(get_db),
):
    """
    Создать новую услугу для текущего мастера.
    """
    service = Service(
        master_id=master.id, name=data.name, duration=data.duration, price=data.price
    )

    db.add(service)
    await db.commit()
    await db.refresh(service)

    logger.info(f"Мастер {master.phone} добавил услугу: {service.name}")

    return service


@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    data: ServiceUpdate,
    master: Master = Depends(get_current_master),
    db: AsyncSession = Depends(get_db),
):
    """
    Обновить услугу по ID. Мастер может обновить только свои услуги.
    """

    result = await db.execute(
        select(Service).where(Service.id == service_id, Service.master_id == master.id)
    )
    service = result.scalar_one_or_none()

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Услуга не найдена"
        )

    if data.name is not None:
        service.name = data.name
    if data.duration is not None:
        service.duration = data.duration
    if data.price is not None:
        service.price = data.price
    if data.is_active is not None:
        service.is_active = data.is_active

    await db.commit()
    await db.refresh(service)

    logger.info(f"Мастер {master.phone} обновил услугу: {service.name}")

    return service


@router.delete("/{service_id}")
async def delete_service(
    service_id: int,
    master: Master = Depends(get_current_master),
    db: AsyncSession = Depends(get_db),
):
    """
    Деактивировать услугу по ID. Услуга не удаляется из БД — только скрывается.
    """

    result = await db.execute(
        select(Service).where(Service.id == service_id, Service.master_id == master.id)
    )

    service = result.scalar_one_or_none()

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Услуга не найдена"
        )

    service.is_active = False

    await db.commit()

    logger.info(f"Мастер {master.phone} удалил услугу: {service.name}")

    return {"detail": "Услуга удалена"}
