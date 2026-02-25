# ai_service.py (UPDATED)
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables.")

        self.client = Groq(api_key=api_key)

        # Recommended stable model
        self.model_name = "llama-3.3-70b-versatile"
        
        self.system_prompt = """
You are 'NepseBot', an expert trading assistant for the Nepal Stock Exchange (NEPSE).

YOUR KNOWLEDGE BASE:
1. Market Hours: Sun-Fri, 11:00 AM - 3:00 PM (Nepal Time).
2. Settlement: T+2 days.
3. Taxes:
   - Capital Gain: 5% (>1 year), 7.5% (<1 year).
   - Dividend: 5% (Cash), 7.5% (Bonus).
4. Circuit Limits: ±10%.
5. Terminology: Kitta, LTP, RO, Crore/Lakhs.

YOUR RULES:
1. Do NOT hallucinate live prices.
2. Always warn about risks.
3. Never guarantee profit.
4. Use market context if provided.
5. Keep response professional and concise.

CURRENT MARKET CONTEXT:
{market_context}
"""

    def chat(self, message, history=None, market_context=""):
        messages = [
            {
                "role": "system",
                "content": self.system_prompt.format(
                    market_context=market_context
                ),
            }
        ]

        if history:
            messages.extend(history[-6:])

        messages.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.3,
            max_tokens=500,
        )

        return response.choices[0].message.content


# ---------------------------------------------------
# GLOBAL INSTANCE (Singleton Pattern)
# ---------------------------------------------------

ai_service = AIService()


# ---------------------------------------------------
# PERMANENT COMPATIBILITY FUNCTION
# ---------------------------------------------------

def get_trade_signal(message, history=None, market_context=""):
    """
    This wrapper ensures backward compatibility.
    Your app.py can safely import this forever.
    """
    return ai_service.chat(
        message=message,
        history=history,
        market_context=market_context
    )