from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.security import hash_password,verify_password,create_access_token,create_refresh_token
from core.logging import get_logger
from models.user import Master
from models.subscription import Subscription
from schemas.auth import MasterRegister, MasterLogin, TokenResponse, MasterResponse
from slugify import slugify

router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger(__name__)

async def  generate_slug(name:str, db:AsyncSession)-> str:
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

async def register(data: MasterRegister, db:AsyncSession = Depends(get_db)):
    result = await db.execute(select(Master).where(Master.phone==data.phone))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Мастер с таким телефоном уже существует")
    
    slug = await generate_slug(data.name, db)

    master = Master(
        name=data.name,
        phone=data.phone,
        password_hash=hash_password(data.password),
        slug=slug
    )
    db.add(master)
    await db.commit()
    await db.refresh(master)

    subscription = Subscription(
        master_id=master.id,
        plan="free",
        is_active=True 
    )

    db.add(subscription)
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
            detail="Неверный телефон или пароль"
        )
    
    if not master.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт заблокирован"
        )
    
    access_token = create_access_token({"sub": str(master.id)})
    refresh_token = create_refresh_token({"sub": str(master.id)})

    logger.info(f"Мастер вошёл: {master.phone}")
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

