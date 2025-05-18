"""
pytest configuration file
"""
import pytest


@pytest.fixture(autouse=True)
def mock_environ(monkeypatch):
    """Fixture to set up environment variables for testing"""
    # Set up fake environment variables to avoid loading from .env files
    monkeypatch.setenv("LOGLEVEL", "INFO")
    monkeypatch.setenv("SPOTIPY_CLIENT_ID", "fake_client_id")
    monkeypatch.setenv("SPOTIPY_CLIENT_SECRET", "fake_client_secret")
    monkeypatch.setenv("OPENAI_API_KEY", "fake_api_key")
