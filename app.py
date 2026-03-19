# app.py
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import logging

from nepse_data import nepse_fetcher
from chat_service import generate_bot_reply
from utils import extract_stock_symbol

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TradeMind — NEPSE Chatbot")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

BOT_NAME = "TradeMind"
MAX_MESSAGE_LENGTH = 500
MAX_HISTORY_LENGTH = 20

chat_sessions: dict[str, list[dict]] = {}


def get_session(session_id: str) -> list[dict]:
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    return chat_sessions[session_id]


def save_session(session_id: str, history: list[dict]) -> None:
    chat_sessions[session_id] = history[-MAX_HISTORY_LENGTH:]


def sanitize(text: str) -> str:
    return text.strip()[:MAX_MESSAGE_LENGTH]


class ChatRequest(BaseModel):
    message:    str = Field(..., min_length=1, max_length=MAX_MESSAGE_LENGTH)
    symbol:     str = Field(default="NABIL", max_length=10)
    session_id: str = Field(default="default")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, session_id: str = "default"):
    return templates.TemplateResponse("index.html", {
        "request":    request,
        "bot_name":   BOT_NAME,
        "chat":       get_session(session_id),
        "summary":    None,
        "trend":      None,
        "session_id": session_id,
    })


@app.get("/api/market")
async def api_market():
    try:
        return JSONResponse({
            "summary": nepse_fetcher.get_market_summary(),
            "trend":   nepse_fetcher.get_market_trend(),
            "index":   nepse_fetcher.get_nepse_index(),
            "status":  nepse_fetcher.get_market_status(),
        })
    except Exception as e:
        return JSONResponse(
            {"error": "NEPSE data temporarily unavailable.", "detail": str(e)},
            status_code=503
        )


@app.post("/chat", response_class=HTMLResponse)
async def chat(
    request: Request,
    message: str = Form(...),
    session_id: str = Form(default="default"),
):
    message = sanitize(message)
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    history     = get_session(session_id)
    symbol      = extract_stock_symbol(message, fallback="NABIL")
    market_data = {}
    bot_text    = ""

    try:
        reply       = generate_bot_reply(
                          message=message,
                          symbol=symbol,
                          history=history,
                      )
        bot_text    = reply.get("reasoning", "Sorry, I could not generate a response.")
        market_data = reply.get("market", {})

    except Exception as e:
        logger.error(f"generate_bot_reply failed: {e}")
        bot_text = f"Sorry, something went wrong: {str(e)}"

    history.append({"role": "user", "text": message})
    history.append({"role": "bot",  "text": bot_text})
    save_session(session_id, history)

    return templates.TemplateResponse("index.html", {
        "request":    request,
        "bot_name":   BOT_NAME,
        "chat":       chat_sessions[session_id],
        "summary":    market_data.get("summary"),
        "trend":      market_data.get("trend"),
        "session_id": session_id,
    })


@app.post("/api/chat")
async def api_chat(payload: ChatRequest):
    message = sanitize(payload.message)
    symbol  = extract_stock_symbol(message, fallback=payload.symbol)
    history = get_session(payload.session_id)
    try:
        reply = generate_bot_reply(
                    message=message,
                    symbol=symbol,
                    history=history,
                )
        history.append({"role": "user", "text": message})
        history.append({"role": "bot",  "text": reply.get("reasoning", "")})
        save_session(payload.session_id, history)
        return JSONResponse(reply)
    except Exception as e:
        logger.error(f"api_chat error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.delete("/api/chat/history")
async def clear_history(session_id: str = "default"):
    chat_sessions.pop(session_id, None)
    return JSONResponse({"message": f"History cleared for '{session_id}'."})