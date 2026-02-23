from fastapi import FastAPI
from core.logging import setup_logging
import models
from api.auth import router as auth_router

setup_logging()

app = FastAPI(
    title="Master App",
    description="Сервис записи к мастерам",
    version="0.1.0"
    
)

app.include_router(auth_router)