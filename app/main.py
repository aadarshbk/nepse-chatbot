"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import logging
import os

from app.core import settings
from app.api import chat_router

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_title,
    description="Educational chatbot for Nepal Stock Exchange (NEPSE)",
    version="1.0.0",
)

# ✅ Healthcheck route (VERY IMPORTANT for Railway)
@app.get("/")
def health_check():
    return {"status": "running"}

# ✅ Mount static only if exists (prevents crash)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("Static folder mounted")
else:
    logger.warning("Static folder not found, skipping mount")

# Include routers
app.include_router(chat_router)

logger.info(f"App initialized: {settings.app_name}")