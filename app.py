from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv

from nepse_data import nepse_fetcher
from analysis import get_market_data
from ai_service import get_trade_signal
from chat_service import generate_bot_reply

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Templates directory
templates = Jinja2Templates(directory="templates")

# Chat memory (temporary in-memory store)
chat_history = []

# Bot name
BOT_NAME = "TradeMind"


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Render home page with chat history.
    """
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "bot_name": BOT_NAME,
            "chat": chat_history,
            "summary": None,
            "trend": "Unknown"
        }
    )


@app.get("/api/market")
async def api_market():
    """
    Market data API (sidebar or AJAX use).
    """
    return JSONResponse({
        "summary": nepse_fetcher.get_market_summary(),
        "trend": nepse_fetcher.get_market_trend(),
        "index": nepse_fetcher.get_nepse_index(),
        "status": nepse_fetcher.get_market_status()
    })


@app.post("/chat", response_class=HTMLResponse)
async def chat(request: Request, message: str = Form(...)):
    """
    Chat endpoint: get trading signal + AI response.
    """
    symbol = "BOKL"  # Change dynamically if needed

    try:
        # Use shared bot service to get structured reply
        reply = generate_bot_reply(message, symbol)

        signal = reply["signal"]
        confidence = reply["confidence"]
        reasoning = reply["reasoning"]
        market_data = reply["market"]

        formatted_reply = f"""
<div class="signal-card {signal.lower()}">
    <div class="signal-header">
        <span class="signal-badge">{signal}</span>
        <span class="confidence">{confidence} confidence</span>
    </div>
    <div class="reasoning">{reasoning}</div>
</div>
"""
    except Exception as e:
        formatted_reply = f"<div class='error'>Error: {str(e)}</div>"
        market_data = {}

    # Update chat history
    chat_history.append(("You", message))
    chat_history.append((BOT_NAME, formatted_reply))

    # Render template with updated data
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "bot_name": BOT_NAME,
            "chat": chat_history,
            "summary": market_data.get("summary"),
            "trend": market_data.get("trend", "Unknown")
        }
    )


@app.post("/api/chat")
async def api_chat(payload: dict):
    """
    JSON chat endpoint for backend integration.

    Expected body:
    {
        "message": "Should I buy BOKL now?",
        "symbol": "BOKL"  # optional
    }
    """
    message = payload.get("message", "").strip()
    symbol = payload.get("symbol", "BOKL")

    if not message:
        return JSONResponse({"error": "message is required"}, status_code=400)

    try:
        reply = generate_bot_reply(message, symbol)
        return JSONResponse(reply)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)