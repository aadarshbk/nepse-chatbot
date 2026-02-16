from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from analysis import get_market_data
from ai_service import get_trade_signal

app = FastAPI()
templates = Jinja2Templates(directory="templates")

chat_history = []
BOT_NAME = "TradeMind"


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "bot_name": BOT_NAME,
        "chat": chat_history,
        "summary": None,
        "trend": "Unknown"
    })


@app.post("/chat", response_class=HTMLResponse)
async def chat(request: Request, message: str = Form(...)):

    symbol = "BOKL"  # change if needed

    try:
        market_data = get_market_data(symbol)

        ai_result = get_trade_signal(symbol, market_data, message)

        signal = ai_result["signal"]
        confidence = ai_result["confidence"]
        reasoning = ai_result["reasoning"]

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
        formatted_reply = f"Error: {str(e)}"

    chat_history.append(("You", message))
    chat_history.append(("TradeMind", formatted_reply))

    return templates.TemplateResponse("index.html", {
        "request": request,
        "bot_name": BOT_NAME,
        "chat": chat_history,
        "summary": market_data.get("summary") if 'market_data' in locals() else None,
        "trend": market_data.get("trend") if 'market_data' in locals() else "Unknown"
    })
