from fastapi import FastAPI
from core.logging import setup_logging

setup_logging()

app = FastAPI(
    title="Master App",
    description="Сервис записи к мастерам",
    version="0.1.0"
    
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}