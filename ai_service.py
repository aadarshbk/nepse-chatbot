import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def get_trade_signal(symbol: str, market_data: dict, user_message: str):

    summary = market_data["summary"]
    trend = market_data["trend"]

    prompt = f"""
You are an expert stock trading AI.

Stock: {symbol}
Current Price: {summary['close']}
Date: {summary['date']}
Trend: {trend}

User question:
{user_message}

Respond STRICTLY in this JSON format:

{{
  "signal": "BUY or SELL or HOLD",
  "confidence": "LOW or MEDIUM or HIGH",
  "reasoning": "Short explanation"
}}
"""

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a professional trading assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    content = response.choices[0].message.content

    try:
        import json
        return json.loads(content)
    except:
        return {
            "signal": "HOLD",
            "confidence": "LOW",
            "reasoning": "AI response parsing failed."
        }
