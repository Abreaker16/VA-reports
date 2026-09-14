import os
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="Multi-Cloud VA Platform",
    description="Vulnerability Assessment Platform for GCP, AWS, and Azure security services",
    version="2.0.0",
    lifespan=lifespan
)

app.include_router(router, prefix="/api")
