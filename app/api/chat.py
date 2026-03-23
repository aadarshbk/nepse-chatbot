"""Chat API routes with Redis-backed sessions and async support."""
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from aioredis import Redis, from_url
import asyncio
import json
import logging

from app.models import ChatRequest
from app.services import generate_bot_reply
from app.utils import extract_stock_symbol, sanitize
from app.core import settings

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Initialize Redis (async)
redis: Redis | None = None

async def get_redis() -> Redis:
    global redis
    if not redis:
        redis = await from_url(settings.redis_url, decode_responses=True)
    return redis

# Helper functions
async def get_session(session_id: str) -> list[dict]:
    r = await get_redis()
    data = await r.get(f"chat:{session_id}")
    if data:
        return json.loads(data)
    return []

async def save_session(session_id: str, history: list[dict]) -> None:
    r = await get_redis()
    # Keep only last N messages
    trimmed = history[-settings.max_history_length:]
    await r.set(f"chat:{session_id}", json.dumps(trimmed), ex=settings.session_ttl)

def capitalize_first(text: str) -> str:
    return text[0].upper() + text[1:] if text else text

# Routes
@router.get("/", response_class=HTMLResponse)
async def home(request: Request, session_id: str = "default"):
    history = await get_session(session_id)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "bot_name": settings.bot_name,
        "chat": history,
        "summary": None,
        "trend": None,
        "session_id": session_id,
    })

@router.get("/api/market")
async def api_market():
    from app.services import nepse_fetcher
    try:
        # Optional caching: cache for 30 seconds
        r = await get_redis()
        cached = await r.get("market_summary")
        if cached:
            return JSONResponse(json.loads(cached))

        data = {
            "summary": nepse_fetcher.get_market_summary(),
            "trend": nepse_fetcher.get_market_trend(),
            "index": nepse_fetcher.get_nepse_index(),
            "status": nepse_fetcher.get_market_status(),
        }
        await r.set("market_summary", json.dumps(data), ex=30)
        return JSONResponse(data)
    except Exception as e:
        logger.error(f"Market data error: {e}")
        return JSONResponse(
            {"error": "NEPSE data temporarily unavailable.", "detail": str(e)},
            status_code=503
        )

@router.post("/chat", response_class=HTMLResponse)
async def chat_form(request: Request, message: str = Form(...), session_id: str = Form("default")):
    message = sanitize(message)
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    history = await get_session(session_id)
    symbol = extract_stock_symbol(message, fallback=settings.default_symbol)
    market_data = {}
    bot_text = ""

    try:
        reply = await asyncio.to_thread(generate_bot_reply, message=message, symbol=symbol, history=history)
        bot_text = capitalize_first(reply.get("reasoning", "Sorry, I could not generate a response."))
        market_data = reply.get("market", {})
    except Exception as e:
        logger.error(f"Chat error: {e}")
        bot_text = f"Sorry, something went wrong: {str(e)}"

    history.append({"role": "user", "text": message})
    history.append({"role": "bot", "text": bot_text})
    await save_session(session_id, history)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "bot_name": settings.bot_name,
        "chat": history,
        "summary": market_data.get("summary"),
        "trend": market_data.get("trend"),
        "session_id": session_id,
    })

@router.post("/api/chat")
async def api_chat(payload: ChatRequest):
    message = sanitize(payload.message)
    symbol = extract_stock_symbol(message, fallback=payload.symbol)
    history = await get_session(payload.session_id)

    try:
        reply = await asyncio.to_thread(generate_bot_reply, message=message, symbol=symbol, history=history)
        reasoning = capitalize_first(reply.get("reasoning", ""))
        history.append({"role": "user", "text": message})
        history.append({"role": "bot", "text": reasoning})
        await save_session(payload.session_id, history)
        return JSONResponse(reply)
    except Exception as e:
        logger.error(f"API chat error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@router.delete("/api/chat/history")
async def clear_history(session_id: str = "default"):
    r = await get_redis()
    await r.delete(f"chat:{session_id}")
    return JSONResponse({"message": f"History cleared for '{session_id}'."})