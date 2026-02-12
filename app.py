from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from functools import lru_cache
import logging

# Import your analysis functions
from analysis import get_summary, get_trend, get_signal

# --------------------------------------------------
# App Configuration
# --------------------------------------------------

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="super_secret_key")

templates = Jinja2Templates(directory="templates")

BOT_NAME = "TradeMind"

logging.basicConfig(level=logging.INFO)


# --------------------------------------------------
# Optional Caching (Avoid repeated NEPSE calls)
# --------------------------------------------------

@lru_cache(maxsize=32)
def cached_summary(symbol: str):
    return get_summary(symbol)


@lru_cache(maxsize=32)
def cached_trend(symbol: str):
    return get_trend(symbol)


@lru_cache(maxsize=32)
def cached_signal(symbol: str):
    return get_signal(symbol)


# --------------------------------------------------
# Helper: Extract Stock Symbol
# --------------------------------------------------

def extract_symbol(message: str):
    words = message.strip().split()
    if len(words) > 1:
        return words[-1].upper()
    return "NABIL"  # Default stock


# --------------------------------------------------
# Trading Bot Brain
# --------------------------------------------------

def generate_reply(message: str):
    message_lower = message.lower()

    try:
        symbol = extract_symbol(message)

        if "summary" in message_lower:
            s = cached_summary(symbol)
            return f"{symbol} latest close price is {s.get('close')} on {s.get('date')}."

        elif "trend" in message_lower:
            t = cached_trend(symbol)
            return f"{symbol} is currently in a {t} trend."

        elif "signal" in message_lower or "trade" in message_lower:
            signal = cached_signal(symbol)
            logging.info(f"Generated signal for {symbol}: {signal}")
            return f"My trading signal for {symbol} is: {signal}"

        else:
            return (
                "Ask me about:\n"
                "- summary NABIL\n"
                "- trend NICA\n"
                "- signal SHIVM"
            )

    except Exception as e:
        logging.error(str(e))
        return "Something went wrong while analyzing the market."


# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    if "chat" not in request.session:
        request.session["chat"] = []

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "chat": request.session["chat"],
            "bot_name": BOT_NAME,
        }
    )


@app.post("/chat", response_class=HTMLResponse)
async def chat(request: Request, message: str = Form(...)):

    chat_history = request.session.get("chat", [])

    reply = generate_reply(message)

    chat_history.append(("You", message))
    chat_history.append((BOT_NAME, reply))

    request.session["chat"] = chat_history

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "chat": chat_history,
            "bot_name": BOT_NAME,
        }
    )
