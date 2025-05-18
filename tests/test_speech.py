"""
Tests for the speech module
"""

from unittest.mock import patch

import pytest

from djgpt.speech import listen, say


@pytest.fixture
def mock_tts():
    """Fixture to mock TTS functionality"""
    with patch("djgpt.speech.TTS") as mock_tts:
        mock_tts.isSpeaking.return_value = False
        yield mock_tts


@pytest.fixture
def mock_console():
    """Fixture to mock rich console"""
    with patch("djgpt.speech.CONSOLE") as mock_console:
        yield mock_console


class TestSpeech:
    """Test speech functionality"""

    def test_say_prints_text(self, mock_console, mock_tts):
        """Test that say prints the text"""
        text = "Hello, world!"
        say(text)
        mock_console.print.assert_called_once_with(text)

    def test_say_with_no_tts(self, mock_console):
        """Test say function when TTS is None"""
        with patch("djgpt.speech.TTS", None):
            with patch("djgpt.speech.TTS_TYPE", None):
                text = "No TTS available"
                say(text)
                mock_console.print.assert_called_once_with(text)
                # Function should return after printing when TTS is None

    @patch("builtins.input", return_value="test input")
    def test_listen_returns_input(self, mock_input, mock_console):
        """Test that listen returns user input"""
        result = listen()
        assert result == "test input"
        mock_console.print.assert_called_once()

    @patch("builtins.input", return_value="")
    def test_listen_empty_input(self, mock_input, mock_console):
        """Test that listen returns None for empty input"""
        result = listen()
        assert result is None

    @patch("builtins.input", side_effect=KeyboardInterrupt)
    def test_listen_keyboard_interrupt(self, mock_input, mock_console):
        """Test that listen handles KeyboardInterrupt"""
        result = listen()
        assert result is None

    @patch("builtins.input", side_effect=Exception("Test error"))
    def test_listen_exception(self, mock_input, mock_console):
        """Test that listen handles general exceptions"""
        result = listen()
        assert result is None
        mock_console.log.assert_called_once()
