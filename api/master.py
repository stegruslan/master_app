from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.dependencies import get_current_master
from core.logging import get_logger
from models.user import Master
from schemas.master import MasterResponse, MasterUpdate


router = APIRouter(prefix="/master", tags=["master"])
logger = get_logger(__name__)


@router.get("/me", response_model=MasterResponse)
async def get_me(master: Master = Depends(get_current_master)):
    """Получить профиль текущего мастера."""

    return master


@router.put("/me", response_model=MasterResponse)
async def update_me(
    data: MasterUpdate,
    master: Master = Depends(get_current_master),
    db: AsyncSession = Depends(get_db),
):
    """Обновить профиль мастера."""

    if data.name is not None:
        master.name = data.name
    if data.email is not None:
        master.email = data.email
    if data.telegram_id is not None:
        master.telegram_id = data.telegram_id

    await db.commit()
    await db.refresh(master)

    logger.info(f"Мастер обновил профиль: {master.phone}")
    return master
