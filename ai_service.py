# ai_service.py (UPDATED)
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # ✅ UPDATED: Use supported model
        # llama-3.3-70b-versatile is the recommended replacement
        self.model_name = "llama-3.3-70b-versatile"
        
        self.system_prompt = """
You are 'NepseBot', an expert trading assistant for the Nepal Stock Exchange (NEPSE).

YOUR KNOWLEDGE BASE:
1. Market Hours: Sun-Fri, 11:00 AM - 3:00 PM (Nepal Time).
2. Settlement: T+2 days (Trade day + 2 working days).
3. Taxes: 
   - Capital Gain: 5% (holding >1 year), 7.5% (holding <1 year).
   - Dividend: 5% (Cash), 7.5% (Bonus).
4. Circuit Limits: Generally ±10% of previous close.
5. Terminology: Kitta (Shares), Crore/Lakhs (Currency), LTP (Last Traded Price), RO (Registered Owner).

YOUR RULES:
1. ACCURACY: Do not hallucinate prices. If unsure, advise checking TMS.
2. SAFETY: Always warn about market risks. Never guarantee profit.
3. TONE: Professional, concise, financial analyst style.
4. CONTEXT: Use provided market data if available in the prompt.
5. LANGUAGE: English, but use Nepali financial terms where appropriate.

CURRENT MARKET CONTEXT:
{market_context}
"""

    def chat(self, message, history=None, market_context=""):
        messages = [
            {"role": "system", "content": self.system_prompt.format(market_context=market_context)}
        ]
        
        # Add history (limit to last 6 messages to save tokens/speed)
        if history:
            messages.extend(history[-6:])
            
        messages.append({"role": "user", "content": message})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,  # ✅ Uses updated model
                messages=messages,
                temperature=0.3,  # Low for factual accuracy
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error connecting to AI: {str(e)}"

# Global instance
ai_service = AIService()