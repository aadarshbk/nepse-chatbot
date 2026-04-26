# app/api/chat.py
"""Chat API routes without Redis dependency."""
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import logging

from app.models import ChatRequest
from app.services.chat_service import generate_bot_reply
from app.utils import extract_stock_symbol, sanitize
from app.core import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory chat sessions (works without Redis)
chat_sessions: dict[str, list[dict]] = {}
templates = Jinja2Templates(directory="templates")


def get_session(session_id: str) -> list[dict]:
    """Get or create chat session."""
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    return chat_sessions[session_id]


def save_session(session_id: str, history: list[dict]) -> None:
    """Save session with max history limit."""
    chat_sessions[session_id] = history[-settings.max_history_length:]


# ✅ NEW: Serve chat.html at GET /chat (fixes 405 error)
@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, session_id: str = "default"):
    """Render the chat UI from chat.html."""
    return templates.TemplateResponse("chat.html", {
        "request":    request,
        "bot_name":   settings.bot_name,
        "chat":       get_session(session_id),
        "summary":    None,
        "trend":      None,
        "session_id": session_id,
    })


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, session_id: str = "default"):
    """Render home page with chat interface."""
    return templates.TemplateResponse("index.html", {
        "request":    request,
        "bot_name":   settings.bot_name,
        "chat":       get_session(session_id),
        "summary":    None,
        "trend":      None,
        "session_id": session_id,
    })


@router.post("/chat", response_class=HTMLResponse)
async def chat_form(
    request: Request,
    message: str = Form(...),
    session_id: str = Form(default="default"),
):
    """Handle chat form submission."""
    message = sanitize(message)
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    history = get_session(session_id)
    symbol  = extract_stock_symbol(message, fallback="NABIL")

    try:
        reply = generate_bot_reply(
            message=message,
            symbol=symbol,
            history=history
        )
        bot_text    = reply.get("reasoning", "Sorry, I could not generate a response.")
        market_data = reply.get("market", {})

    except Exception as e:
        logger.error(f"Chat error: {e}")
        bot_text = f"Sorry, something went wrong: {str(e)}"
        market_data = {}

    # Capitalize first letter
    bot_text = bot_text[0].upper() + bot_text[1:] if bot_text else bot_text

    history.append({"role": "user", "text": message})
    history.append({"role": "bot",  "text": bot_text})
    save_session(session_id, history)

    return templates.TemplateResponse("index.html", {
        "request":    request,
        "bot_name":   settings.bot_name,
        "chat":       chat_sessions[session_id],
        "summary":    market_data.get("summary"),
        "trend":      market_data.get("trend"),
        "session_id": session_id,
    })


@router.post("/api/chat")
async def api_chat(payload: ChatRequest):
    """Handle API chat request."""
    message = sanitize(payload.message)
    symbol  = extract_stock_symbol(message, fallback=payload.symbol)
    history = get_session(payload.session_id)

    try:
        reply = generate_bot_reply(
            message=message,
            symbol=symbol,
            history=history
        )
        reasoning = reply.get("reasoning", "")
        if reasoning:
            reasoning = reasoning[0].upper() + reasoning[1:]

        history.append({"role": "user", "text": message})
        history.append({"role": "bot",  "text": reasoning})
        save_session(payload.session_id, history)
        return JSONResponse(reply)

    except Exception as e:
        logger.error(f"API chat error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@router.delete("/api/chat/history")
async def clear_history(session_id: str = "default"):
    """Clear chat history for session."""
    chat_sessions.pop(session_id, None)
    return JSONResponse({"message": f"History cleared for '{session_id}'."})