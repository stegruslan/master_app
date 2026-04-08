from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_access_token,
)
from core.logging import get_logger
from models.user import Master
from models.subscription import Subscription
from models.schedule import WorkSchedule
from schemas.auth import (
    MasterRegister,
    MasterLogin,
    TokenResponse,
    RefreshTokenRequest,
)
from schemas.master import MasterResponse
from slugify import slugify
from datetime import time
from schemas.auth import (
    MasterRegister,
    MasterLogin,
    TokenResponse,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from models.password_reset import PasswordResetToken
from utils.email import send_password_reset_email
from datetime import time, datetime, timedelta, timezone
import secrets
from core.config import settings


router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger(__name__)


async def generate_slug(name: str, db: AsyncSession) -> str:
    base_slug = slugify(name)
    slug = base_slug
    counter = 2
    while True:
        result = await db.execute(select(Master).where(Master.slug == slug))
        if not result.scalar_one_or_none():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


@router.post("/register", response_model=MasterResponse)
async def register(data: MasterRegister, db: AsyncSession = Depends(get_db)):
    # проверка телефона
    result = await db.execute(select(Master).where(Master.phone == data.phone))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Мастер с таким телефоном уже существует",
        )
    # проверка email
    result = await db.execute(select(Master).where(Master.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Мастер с таким email уже существует",
        )

    slug = await generate_slug(data.name, db)

    master = Master(
        name=data.name,
        phone=data.phone,
        password_hash=hash_password(data.password),
        slug=slug,
        email=data.email,
    )
    db.add(master)
    await db.commit()
    await db.refresh(master)

    # создается бесплатная подписка
    subscription = Subscription(master_id=master.id, plan="free", is_active=True)
    db.add(subscription)

    for weekday in range(7):
        schedule = WorkSchedule(
            master_id=master.id,
            weekday=weekday,
            start_time=time(9, 0),
            end_time=time(18, 0),
            is_working=True,
        )
        db.add(schedule)
    await db.commit()

    logger.info(f"Зарегистрировался новый мастер: {master.phone}")

    return master


@router.post("/login", response_model=TokenResponse)
async def login(data: MasterLogin, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Master).where(Master.phone == data.phone))
    master = result.scalar_one_or_none()

    if not master or not verify_password(data.password, master.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный телефон или пароль",
        )

    if not master.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Аккаунт заблокирован"
        )

    access_token = create_access_token({"sub": str(master.id)})
    refresh_token = create_refresh_token({"sub": str(master.id)})

    logger.info(f"Мастер вошёл: {master.phone}")
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Обновить access токен через refresh токен."""

    payload = decode_access_token(data.refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный или истёкший refresh токен",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный тип токена"
        )

    master_id = payload.get("sub")
    if master_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен"
        )

    result = await db.execute(select(Master).where(Master.id == int(master_id)))

    master = result.scalar_one_or_none()

    if master is None or not master.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Мастер не найден или заблокирован",
        )

    access_token = create_access_token({"sub": str(master_id)})
    refresh_token = create_refresh_token({"sub": str(master_id)})

    logger.info(f"Мастер обновил токен: {master.phone}")
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)
):
    """Запросить сброс пароля — отправляет письмо на email."""
    result = await db.execute(select(Master).where(Master.email == data.email))
    master = result.scalar_one_or_none()

    if not master:
        # Не раскрываем существует ли email — всегда отвечаем одинаково
        return {"detail": "Если email зарегистрирован — письмо отправлено"}

    # Инвалидируем старые токены
    old_tokens = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.master_id == master.id,
            PasswordResetToken.used == False,
        )
    )

    for token in old_tokens.scalars().all():
        token.used = True

    # Создаём новый токен
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    reset_token = PasswordResetToken(
        master_id=master.id,
        token=token,
        expires_at=expires_at,
    )

    db.add(reset_token)
    await db.commit()

    reset_url = f"{settings.FRONTEND_URL}/reset?token={token}"
    await send_password_reset_email(master.email, reset_url)

    logger.info(f"Запрос сброса пароля для: {master.email}")
    return {"detail": "Если email зарегистрирован — письмо отправлено"}


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)
):
    """Сбросить пароль по токену из письма."""
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == data.token, PasswordResetToken.used == False
        )
    )

    reset_token = result.scalar_one_or_none()

    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недействительная или уже использованная ссылка",
        )

    expires_at = reset_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ссылка истекла. Запросите новую.",
        )

    # Меняем пароль
    result = await db.execute(select(Master).where(Master.id == reset_token.master_id))
    master = result.scalar_one()
    master.password_hash = hash_password(data.new_password)

    # Помечаем токен использованным
    reset_token.used = True

    await db.commit()

    logger.info(f"Пароль сброшен для мастера id={master.id}")
    return {"detail": "Пароль успешно изменён"}
