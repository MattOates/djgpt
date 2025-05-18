import os
from unittest import mock

import pytest


# Define fixtures to mock API calls
@pytest.fixture
def mock_spotify_api():
    """Mock for Spotify API calls"""
    with mock.patch("djgpt.spotify.get_spotify") as mocked_get_spotify:
        # Return a mock object that can be used in place of the Spotify client
        mocked_client = mock.MagicMock()
        mocked_get_spotify.return_value = mocked_client

        # Configure the mock to return sensible values for common methods
        mocked_client.devices.return_value = {
            "devices": [{"id": "mock_device_id", "name": "Mock Device", "is_active": True}]
        }

        mocked_client.search.return_value = {
            "tracks": {
                "items": [
                    {
                        "name": "Mock Track",
                        "artists": [{"name": "Mock Artist"}],
                        "external_urls": {"spotify": "https://mock-url"},
                        "uri": "spotify:track:mock123",
                    }
                ]
            }
        }

        yield mocked_client


@pytest.fixture
def mock_openai_api():
    """Mock for OpenAI API calls"""
    with mock.patch("openai.ChatCompletion.create") as mocked_create:
        # Configure the mock to return a fixed response
        mocked_create.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '[{"artist": "Mock Artist", "trackname": "Mock Song", "genre": "Mock Genre", "reason": "For testing", "quality": 0.9}]'
                    }
                }
            ]
        }
        yield mocked_create


# Environment setup for tests
@pytest.fixture(autouse=True)
def mock_env_vars():
    """Set dummy environment variables for testing"""
    with mock.patch.dict(
        os.environ,
        {
            "SPOTIPY_CLIENT_ID": "dummy_spotify_id",
            "SPOTIPY_CLIENT_SECRET": "dummy_spotify_secret",
            "OPENAI_API_KEY": "dummy_openai_key",
        },
    ):
        yield
