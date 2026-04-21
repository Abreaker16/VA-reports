from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="GCP VA Platform")

app.include_router(router, prefix="/api")
