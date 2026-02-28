from fastapi import FastAPI
from fastapi.security import HTTPBearer
from core.logging import setup_logging
from api.auth import router as auth_router
from api.services import router as services_router
from api.schedule import router as schedule_router
from api.bookings import router as bookings_router
from api.public import router as public_router

setup_logging()
security = HTTPBearer()
app = FastAPI(
    title="Master App", description="Сервис записи к мастерам", version="0.1.0"
)

app.include_router(auth_router)
app.include_router(services_router)
app.include_router(schedule_router)
app.include_router(bookings_router)
app.include_router(public_router)
