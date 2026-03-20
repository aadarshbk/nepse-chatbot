# ai_service.py
import os
import time
import logging
from groq import Groq

logger = logging.getLogger(__name__)

# ── Models tried in order — if one is rate limited, next is used ──────────────
MODELS = [
    "llama-3.3-70b-versatile",   # best quality — tried first
    "llama3-70b-8192",            # alternate 70b — separate quota
    "llama3-8b-8192",             # fast + cheap — separate quota
    "gemma2-9b-it",               # Google Gemma — separate quota
    "mixtral-8x7b-32768",         # Mixtral — separate quota
]

MAX_TOKENS        = 400           # reduced to save tokens
TEMPERATURE       = 0.3
MAX_HISTORY_TURNS = 4             # reduced from 6 to save tokens
MAX_RETRIES       = 1             # 1 retry per model before moving to next
RETRY_DELAY_SEC   = 1.0

SYSTEM_PROMPT = """You are TradeMind, a friendly educational trading assistant for the Nepal Stock Exchange (NEPSE).
Your audience is BEGINNER traders learning the stock market for the first time.

NEPSE KNOWLEDGE:
- Market Hours: Sunday to Thursday, 11:00 AM to 3:00 PM NST
- Settlement: T+2 (shares and cash arrive 2 business days after trade)
- Circuit Limit: plus or minus 10% max price move per day
- Capital Gains: held more than 1 year = 5% tax, held 1 year or less = 7.5% tax
- Dividend Tax: Cash dividend = 5%, Bonus shares = 7.5%
- Key Terms: Kitta (1 share unit), LTP (Last Traded Price), RO (Rights Offering)

YOUR RULES:
1. Keep answers SHORT — 3 to 5 sentences maximum.
2. NEVER fabricate live prices — use only the market context provided.
3. Always explain financial terms simply. Assume the user has never invested before.
4. NEVER guarantee profit or say definitively buy or sell.
5. Always mention relevant risks alongside any opportunity.
6. If you do not know something, say so clearly — never guess.
7. Be encouraging — investing is intimidating for beginners.
8. NEVER use markdown formatting. No bold, no italic, no headings, no code blocks.
   Use plain text only. For lists use a plain dash (-). No symbols for emphasis.
9. Always start your response with a capital letter.

CURRENT MARKET CONTEXT:
{market_context}"""


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
                    "GROQ_API_KEY not set. Add it to your .env file."
                )
            self._client = Groq(api_key=api_key)
        return self._client

    def _is_rate_limit(self, error: Exception) -> bool:
        err = str(error).lower()
        return "429" in str(error) or "rate" in err or "too many" in err or "quota" in err or "tokens per day" in err

    def chat(
        self,
        message:        str,
        history:        list[dict] | None = None,
        market_context: str = "No live market data available.",
    ) -> str:
        client = self._get_client()

        messages = [
            {
                "role":    "system",
                "content": SYSTEM_PROMPT.format(market_context=market_context)
            }
        ]

        if history:
            messages.extend(
                _format_history(history[-(MAX_HISTORY_TURNS * 2):])
            )

        messages.append({"role": "user", "content": message})

        last_error = None

        for model in MODELS:
            for attempt in range(1, MAX_RETRIES + 2):
                try:
                    logger.info(f"Trying model: {model} (attempt {attempt})")

                    response = self._client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=TEMPERATURE,
                        max_tokens=MAX_TOKENS,
                    )

                    reply = response.choices[0].message.content
                    if reply and reply.strip():
                        logger.info(f"Success with model: {model}")
                        return reply.strip()

                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"Model {model} attempt {attempt} failed: {e}"
                    )

                    if self._is_rate_limit(e):
                        # Rate limited — skip remaining retries, try next model
                        logger.info(
                            f"Rate limit hit on {model}, switching to next model..."
                        )
                        break

                    if attempt <= MAX_RETRIES:
                        time.sleep(RETRY_DELAY_SEC)

        # All models exhausted
        logger.error(f"All models failed. Last error: {last_error}")
        raise RuntimeError(
            "All AI models are currently rate limited. "
            "Please wait a few minutes and try again."
        )


ai_service = AIService()


def get_trade_signal(
    message:        str,
    history:        list[dict] | None = None,
    market_context: str = "",
) -> str:
    return ai_service.chat(
        message=message,
        history=history,
        market_context=market_context,
    )