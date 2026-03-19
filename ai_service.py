# ai_service.py
import os
import time
import logging
from groq import Groq

logger = logging.getLogger(__name__)

MODEL_NAME        = "llama-3.3-70b-versatile"
MAX_TOKENS        = 800
TEMPERATURE       = 0.3
MAX_HISTORY_TURNS = 6
MAX_RETRIES       = 2
RETRY_DELAY_SEC   = 1.5

SYSTEM_PROMPT = """
You are TradeMind, a friendly educational trading assistant for the Nepal Stock Exchange (NEPSE).
Your audience is BEGINNER traders learning the stock market for the first time.

── NEPSE KNOWLEDGE ─────────────────────────────────────────────────────────────
- Market Hours  : Sunday to Thursday, 11:00 AM to 3:00 PM NST
- Settlement    : T+2 (shares/cash arrive 2 business days after trade)
- Circuit Limit : plus or minus 10% max price move per day
- Capital Gains : held more than 1 year = 5% tax | held 1 year or less = 7.5% tax
- Dividend Tax  : Cash dividend = 5% | Bonus shares = 7.5%
- Key Terms     : Kitta (1 share unit), LTP (Last Traded Price), RO (Rights Offering),
                  Crore/Lakh (Nepali number system)

── YOUR RULES ──────────────────────────────────────────────────────────────────
1. NEVER fabricate live prices — use ONLY the market context provided below.
2. ALWAYS explain financial terms simply. Assume the user has never invested before.
3. NEVER guarantee profit or say definitively buy this or sell this.
4. ALWAYS mention relevant risks alongside any opportunity you discuss.
5. If you do not know something, say so clearly — never guess.
6. Be encouraging — investing is intimidating for beginners, be supportive.
7. NEVER use markdown formatting of any kind in your response.
   This means: no **bold**, no *italic*, no # headings, no ``` code blocks.
   Use plain text only. For lists, use a plain dash (-) at the start of each line.
   For emphasis, just write the word normally — do not wrap it in any symbols.

── CURRENT MARKET CONTEXT ──────────────────────────────────────────────────────
{market_context}
"""


def _format_history(history: list[dict]) -> list[dict]:
    result = []
    for entry in history:
        text = entry.get("text", "").strip()
        if not text:
            continue
        role = "assistant" if entry.get("role") == "bot" else "user"
        result.append({"role": role, "content": text})
    return result


class AIService:
    def __init__(self):
        self._client: Groq | None = None

    def _get_client(self) -> Groq:
        if self._client is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise EnvironmentError(
                    "GROQ_API_KEY not set. Add it to your .env file: GROQ_API_KEY=your_key_here"
                )
            self._client = Groq(api_key=api_key)
        return self._client

    def chat(
        self,
        message: str,
        history: list[dict] | None = None,
        market_context: str = "No live market data available.",
    ) -> str:
        client   = self._get_client()
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT.format(market_context=market_context)
            }
        ]

        if history:
            messages.extend(_format_history(history[-(MAX_HISTORY_TURNS * 2):]))

        messages.append({"role": "user", "content": message})

        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS,
                )
                reply = response.choices[0].message.content
                if not reply or not reply.strip():
                    return "I could not generate a response. Please try rephrasing your question."
                return reply.strip()
            except Exception as e:
                last_error = e
                logger.warning(f"Groq attempt {attempt}/{MAX_RETRIES} failed: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY_SEC)

        raise RuntimeError("AI service is temporarily unavailable. Please try again shortly.")


ai_service = AIService()


def get_trade_signal(
    message: str,
    history: list[dict] | None = None,
    market_context: str = "",
) -> str:
    return ai_service.chat(
        message=message,
        history=history,
        market_context=market_context,
    )