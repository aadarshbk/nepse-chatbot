"""Market API router."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.nepse_service import nepse_fetcher

router = APIRouter()

@router.get("/api/market")
async def get_market():
    return JSONResponse(nepse_fetcher.get_market_summary())