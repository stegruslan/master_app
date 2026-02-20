from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)

engine = create_async_engine(settings.DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine,class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session() as session:
        try:
            yield session
            logger.info("Сессия БД открыта")
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка сессии БД: {e}", exc_info=True)
            raise
        finally:
            await session.close()