"""
Tests for the spotify module
"""

from unittest.mock import MagicMock, patch

import pytest

from djgpt.spotify import Spotify, Track, search_spotify


@pytest.fixture
def mock_spotify_api():
    """Fixture to mock Spotify API calls"""
    with patch("djgpt.spotify.get_spotify") as mock_get_spotify:
        mock_spotify = MagicMock()
        mock_get_spotify.return_value = mock_spotify
        yield mock_spotify


class TestTrack:
    """Test Track functionality"""

    def test_track_creation(self):
        """Test creating a Track object"""
        track = Track(artist="Test Artist", trackname="Test Track")
        assert track.artist == "Test Artist"
        assert track.trackname == "Test Track"
        assert track.genre is None
        assert track.reason is None
        assert track.quality is None
        assert track.error is None

    def test_track_with_optional_fields(self):
        """Test creating a Track with optional fields"""
        track = Track(
            artist="Test Artist",
            trackname="Test Track",
            genre="Test Genre",
            reason="Test Reason",
            quality=0.8,
            error="Test Error",
        )
        assert track.artist == "Test Artist"
        assert track.trackname == "Test Track"
        assert track.genre == "Test Genre"
        assert track.reason == "Test Reason"
        assert track.quality == 0.8
        assert track.error == "Test Error"


class TestSpotifySearch:
    """Test Spotify search functionality"""

    @patch("djgpt.spotify.search_spotify")
    def test_track_spotify_property(self, mock_search):
        """Test the spotify property of Track"""
        # Setup mock return value
        mock_spotify = Spotify(
            url="https://open.spotify.com/track/123", uri="spotify:track:123", stash={}
        )
        mock_search.return_value = mock_spotify

        # Create a track and test its spotify property
        track = Track(artist="Test Artist", trackname="Test Track")
        spotify_result = track.spotify

        # Assert search_spotify was called with the right arguments
        mock_search.assert_called_once_with("Test Artist", "Test Track")

        # Assert that the spotify property returns the expected Spotify object
        assert spotify_result == mock_spotify
        assert spotify_result.url == "https://open.spotify.com/track/123"
        assert spotify_result.uri == "spotify:track:123"

    def test_search_spotify(self, mock_spotify_api):
        """Test search_spotify function"""
        # Setup mock response
        mock_spotify_api.search.return_value = {
            "tracks": {
                "items": [
                    {
                        "external_urls": {"spotify": "https://open.spotify.com/track/123"},
                        "uri": "spotify:track:123",
                    }
                ]
            }
        }

        # Call the function
        result = search_spotify("Test Artist", "Test Track")

        # Assert the Spotify API was called with correct query
        mock_spotify_api.search.assert_called_once_with(
            "artist:Test Artist track:Test Track", limit=1, offset=0, type="track"
        )

        # Assert the result is as expected
        assert isinstance(result, Spotify)
        assert result.url == "https://open.spotify.com/track/123"
        assert result.uri == "spotify:track:123"

    def test_search_spotify_no_results(self, mock_spotify_api):
        """Test search_spotify function when no results are found"""
        # Setup mock response with no items
        mock_spotify_api.search.return_value = {"tracks": {"items": []}}

        # Call the function
        result = search_spotify("Nonexistent Artist", "Nonexistent Track")

        # Assert the result is None
        assert result is None

    def test_search_spotify_error(self, mock_spotify_api):
        """Test search_spotify function when an error occurs"""
        # Setup mock to raise an exception
        mock_spotify_api.search.side_effect = Exception("Test error")

        # Call the function
        result = search_spotify("Test Artist", "Test Track")

        # Assert the result is None
        assert result is None
