from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from analysis import get_summary, get_trend

app = FastAPI()
templates = Jinja2Templates(directory="templates")

BOT_NAME = "TradeMind"

chat_history = []


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    s = get_summary()
    t = get_trend()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "chat": chat_history, "bot_name": BOT_NAME, "summary": s, "trend": t}
    )


@app.post("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    form = await request.form()
    user_msg = form.get("message")

    reply = "I didn't understand that."

    if user_msg:
        if "summary" in user_msg.lower():
            s = get_summary()
            reply = f"Latest close price is {s.get('close')} on {s.get('date')}"

        elif "trend" in user_msg.lower():
            t = get_trend()
            reply = f"The stock is in a {t} based on recent days."

    chat_history.append(("You", user_msg))
    chat_history.append((BOT_NAME, reply))

    s = get_summary()
    t = get_trend()

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "chat": chat_history, "bot_name": BOT_NAME, "summary": s, "trend": t}
    )
