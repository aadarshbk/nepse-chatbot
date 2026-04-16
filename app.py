# app.py
import os
import logging

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from app.services.nepse_service import nepse_fetcher
from app.services.chat_service import generate_bot_reply
from app.utils.helpers import extract_stock_symbol

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TradeMind — NEPSE Chatbot")

# ---------- SAFE PATHS FOR RENDER ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)

templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "templates")
)

# ---------- CONFIG ----------
BOT_NAME = "TradeMind"
MAX_MESSAGE_LENGTH = 500
MAX_HISTORY_LENGTH = 20

chat_sessions: dict[str, list[dict]] = {}

# ---------- SESSION ----------
def get_session(session_id: str) -> list[dict]:
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    return chat_sessions[session_id]

def save_session(session_id: str, history: list[dict]) -> None:
    chat_sessions[session_id] = history[-MAX_HISTORY_LENGTH:]

def sanitize(text: str) -> str:
    return text.strip()[:MAX_MESSAGE_LENGTH]

# ---------- REQUEST MODEL ----------
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=MAX_MESSAGE_LENGTH)
    symbol: str = Field(default="NABIL", max_length=10)
    session_id: str = Field(default="default")

# ---------- HOME ROUTE (HEAD FIX INCLUDED) ----------
@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def home(request: Request, session_id: str = "default"):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "bot_name": BOT_NAME,
        "chat": get_session(session_id),
        "summary": None,
        "trend": None,
        "session_id": session_id,
    })

# ---------- MARKET ----------
#

# ---------- CHAT FORM ----------
@app.post("/chat", response_class=HTMLResponse)
async def chat(
    request: Request,
    message: str = Form(...),
    session_id: str = Form(default="default"),
):
    message = sanitize(message)

    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    history = get_session(session_id)
    symbol = extract_stock_symbol(message, fallback="NABIL")

    market_data = {}
    bot_text = ""

    try:
        reply = generate_bot_reply(
            message=message,
            symbol=symbol,
            history=history,
        )

        bot_text = reply.get("reasoning", "Sorry, I would not be able to generate a response.Thank you for your understanding.")
        market_data = reply.get("market", {})

    except Exception as e:
        logger.error(f"generate_bot_reply failed: {e}")
        bot_text = f"Sorry, something went wrong: {str(e)}"

    if bot_text:
        bot_text = bot_text[0].upper() + bot_text[1:]

    history.append({"role": "user", "text": message})
    history.append({"role": "bot", "text": bot_text})
    save_session(session_id, history)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "bot_name": BOT_NAME,
        "chat": chat_sessions[session_id],
        "summary": market_data.get("summary"),
        "trend": market_data.get("trend"),
        "session_id": session_id,
    })

# ---------- API CHAT ----------
@app.post("/api/chat")
async def api_chat(payload: ChatRequest):
    message = sanitize(payload.message)
    symbol = extract_stock_symbol(message, fallback=payload.symbol)
    history = get_session(payload.session_id)

    try:
        reply = generate_bot_reply(
            message=message,
            symbol=symbol,
            history=history,
        )

        reasoning = reply.get("reasoning", "")
        if reasoning:
            reasoning = reasoning[0].upper() + reasoning[1:]

        history.append({"role": "user", "text": message})
        history.append({"role": "bot", "text": reasoning})
        save_session(payload.session_id, history)

        return JSONResponse(reply)

    except Exception as e:
        logger.error(f"api_chat error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

# ---------- CLEAR HISTORY ----------
@app.delete("/api/chat/history")
async def clear_history(session_id: str = "default"):
    chat_sessions.pop(session_id, None)
    return JSONResponse({"message": f"History cleared for '{session_id}'."})

# ---------- MARKET API ----------
@app.get("/api/market")
async def get_market():
    return JSONResponse(nepse_fetcher.get_market_summary())