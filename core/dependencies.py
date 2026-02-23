from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.security import decode_access_token
from core.logging import get_logger
from models.user import Master


logger = get_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_master(token:str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db))-> Master:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        logger.warning("Попытка доступа с невалидным токеном")
        raise credentials_exception
    
    master_id = payload.get("sub")
    if master_id is None:
        raise credentials_exception
    
    result = await db.execute(select(Master).where(Master.id == int(master_id)))
    master = result.scalar_one_or_none()

    if master is None:
        raise credentials_exception
    
    if not master.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт заблокирован"
        )
    
    return master