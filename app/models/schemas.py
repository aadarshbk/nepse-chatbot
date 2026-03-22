"""Pydantic models and schemas for request/response validation."""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat request schema."""
    
    message: str = Field(..., min_length=1, max_length=500)
    symbol: str = Field(default="NABIL", max_length=10)
    session_id: str = Field(default="default")


class ChatMessage(BaseModel):
    """Individual chat message."""
    
    role: str  # "user" or "bot"
    text: str


class ChatResponse(BaseModel):
    """Chat response schema."""
    
    bot_name: str
    symbol: str
    reasoning: str
    market: dict = Field(default_factory=dict)


class MarketDataResponse(BaseModel):
    """Market data response schema."""
    
    summary: str | None = None
    trend: str | None = None
    index: str | None = None
    status: str | None = None


class HistoryClearResponse(BaseModel):
    """Response for history clearing."""
    
    message: str
