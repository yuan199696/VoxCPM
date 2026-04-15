"""FastAPI main application"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import tts, health
from .config import APISettings


settings = APISettings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    yield


app = FastAPI(
    title="VoxCPM API",
    description="HTTP API for VoxCPM Text-to-Speech synthesis",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tts.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "VoxCPM API",
        "version": "1.0.0",
        "docs": "/docs",
    }
