"""Test fixtures and configuration."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_message():
    """Sample chat message for testing."""
    return "What is NABIL stock about?"
