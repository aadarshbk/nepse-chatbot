# app/api/chat.py
"""Chat API routes without Redis dependency."""
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import logging
import asyncio
import os
from copy import deepcopy

from app.models import ChatRequest
from app.services import generate_bot_reply
from app.utils import extract_stock_symbol, sanitize
from app.core import settings

logger = logging.getLogger(__name__)

# ✅ FIX 1: Rename to match main.py import
chat_router = APIRouter()

# ---------------------------
# SAFE PATH FOR TEMPLATES
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "templates"))
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# ---------------------------
# SESSION STORAGE
# ---------------------------
chat_sessions: dict[str, list[dict]] = {}
session_locks: dict[str, asyncio.Lock] = {}


def get_session(session_id: str) -> list[dict]:
    """Get or create session safely."""
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
        session_locks[session_id] = asyncio.Lock()
    return chat_sessions[session_id]


async def save_session(session_id: str, history: list[dict]) -> None:
    """Thread-safe session saving with limit."""
    lock = session_locks.setdefault(session_id, asyncio.Lock())
    async with lock:
        chat_sessions[session_id] = history[-settings.max_history_length:]


def safe_context(**kwargs):
    """Prevent Jinja mutation issues."""
    return {
        k: deepcopy(v) if isinstance(v, (list, dict))
        else ("" if v is None else v)
        for k, v in kwargs.items()
    }


def format_text(text: str) -> str:
    """Safe capitalization."""
    text = (text or "").strip()
    return text[:1].upper() + text[1:] if text else ""


# ---------------------------
# ✅ FIX 2: NEW ROUTE - Serve chat.html at GET /chat
# ---------------------------
@chat_router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, session_id: str = "default"):
    """Render the chat UI from chat.html."""
    history = get_session(session_id)
    return templates.TemplateResponse(
        safe_context(
            request=request,
            bot_name=settings.bot_name,
            chat=history,
            summary="",
            trend="",
            session_id=session_id,
        ),
        "chat.html",  # ✅ Serve your new UI
    )


# ---------------------------
# HOME PAGE
# ---------------------------
@chat_router.get("/", response_class=HTMLResponse)
async def home(request: Request, session_id: str = "default"):
    history = get_session(session_id)

    return templates.TemplateResponse(
        safe_context(
            request=request,
            bot_name=settings.bot_name,
            chat=history,
            summary="",
            trend="",
            session_id=session_id,
        ),
        "index.html",
    )


# ---------------------------
# HTML CHAT (Form fallback)
# ---------------------------
@chat_router.post("/chat", response_class=HTMLResponse)
async def chat_form(
    request: Request,
    message: str = Form(...),
    session_id: str = Form(default="default"),
):
    message = sanitize(message)

    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    history = get_session(session_id)
    symbol = extract_stock_symbol(message, fallback="NABIL")

    try:
        # ⚡ NON-BLOCKING CALL
        reply = await asyncio.to_thread(
            generate_bot_reply,
            message=message,
            symbol=symbol,
            history=history,
        )

        bot_text = format_text(
            reply.get("reasoning", "Sorry, I could not generate a response.")
        )
        market_data = reply.get("market", {})

    except Exception as e:
        logger.exception("Chat error")
        bot_text = f"Sorry, something went wrong."

    history.extend([
        {"role": "user", "text": message},
        {"role": "bot", "text": bot_text},
    ])

    await save_session(session_id, history)

    return templates.TemplateResponse(
        safe_context(
            request=request,
            bot_name=settings.bot_name,
            chat=history,
            summary=market_data.get("summary", ""),
            trend=market_data.get("trend", ""),
            session_id=session_id,
        ),
        "index.html",  # Keep index.html for form fallback
    )


# ---------------------------
# API CHAT (JSON) - Used by your JavaScript frontend
# ---------------------------
@chat_router.post("/api/chat")
async def api_chat(payload: ChatRequest):
    message = sanitize(payload.message)

    if not message:
        return JSONResponse({"error": "Empty message"}, status_code=400)

    history = get_session(payload.session_id)
    symbol = extract_stock_symbol(message, fallback=payload.symbol)

    try:
        reply = await asyncio.to_thread(
            generate_bot_reply,
            message=message,
            symbol=symbol,
            history=history,
        )

        reasoning = format_text(reply.get("reasoning", ""))

        history.extend([
            {"role": "user", "text": message},
            {"role": "bot", "text": reasoning},
        ])

        await save_session(payload.session_id, history)

        return JSONResponse(reply)

    except Exception as e:
        logger.exception("API chat error")
        return JSONResponse(
            {"error": "Internal server error"},
            status_code=500,
        )


# ---------------------------
# CLEAR HISTORY
# ---------------------------
@chat_router.delete("/api/chat/history")
async def clear_history(session_id: str = "default"):
    lock = session_locks.setdefault(session_id, asyncio.Lock())

    async with lock:
        chat_sessions.pop(session_id, None)
        session_locks.pop(session_id, None)

    return JSONResponse({"message": f"History cleared for '{session_id}'"})