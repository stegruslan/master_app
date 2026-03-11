from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from core.logging import setup_logging
from core.config import settings
from api.auth import router as auth_router
from api.master import router as master_router
from api.services import router as services_router
from api.schedule import router as schedule_router
from api.bookings import router as bookings_router
from api.public import router as public_router
from admin.setup import setup_admin


setup_logging(debug=settings.DEBUG)
security = HTTPBearer()
app = FastAPI(
    title="Master App", description="Сервис записи к специалистам", version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(master_router)
app.include_router(services_router)
app.include_router(schedule_router)
app.include_router(bookings_router)
app.include_router(public_router)


setup_admin(app)
