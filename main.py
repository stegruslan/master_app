from fastapi import FastAPI
from core.logging import setup_logging

setup_logging()

app = FastAPI()