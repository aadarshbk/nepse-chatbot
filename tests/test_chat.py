"""Chat API tests."""
import pytest
from app.api.chat import get_session, save_session


def test_home_page(client):
    """Test home page loads."""
    response = client.get("/")
    assert response.status_code == 200
    assert "TradeMind" in response.text


def test_chat_page_exposes_voice_language_choices(client):
    """Test voice language choices are available in the chat UI."""
    response = client.get("/chat")
    assert response.status_code == 200
    assert 'id="voice-language"' in response.text
    assert 'value="unknown">Auto / English' in response.text
    assert 'value="hi-IN">Hindi' in response.text
    assert 'value="te-IN">Telugu' in response.text


def test_market_endpoint(client):
    """Test market data endpoint."""
    response = client.get("/api/market")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_session_management():
    """Test chat session management."""
    session_id = "test-session"
    history = get_session(session_id)
    assert history == []
    
    history.append({"role": "user", "text": "Test message"})
    save_session(session_id, history)
    
    retrieved = get_session(session_id)
    assert len(retrieved) == 1
    assert retrieved[0]["text"] == "Test message"
