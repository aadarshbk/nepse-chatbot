"""Market API router."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.nepse_service import nepse_fetcher

# ✅ CHANGE: router → market_router (to match __init__.py import)
market_router = APIRouter()

@market_router.get("/api/market")  # ✅ CHANGE: @router. → @market_router.
async def get_market():
    return JSONResponse(nepse_fetcher.get_market_summary())