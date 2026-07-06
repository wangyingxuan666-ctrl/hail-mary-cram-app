"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: ensure data directories exist
    settings.get_data_path("vectors")
    settings.get_data_path("sessions")
    settings.get_data_path("uploads")
    print(f"Data directory: {settings.data_dir}")
    print(f"Model: {settings.model_name}")
    yield
    # Shutdown: nothing to clean up


app = FastAPI(
    title="Hail Mary Cram - 临时抱佛脚",
    description="AI-powered exam cramming assistant. Course materials as dictionary, exam papers as main anchor.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register routes
from routes.upload import router as upload_router
from routes.analysis import router as analysis_router
from routes.chat import router as chat_router
from routes.export import router as export_router
from routes.memory import router as memory_router

app.include_router(upload_router)
app.include_router(analysis_router)
app.include_router(chat_router)
app.include_router(export_router)
app.include_router(memory_router)


@app.get("/")
async def root():
    return {
        "name": "Hail Mary Cram - 临时抱佛脚",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api/health")
async def health():
    return {"status": "ok"}
