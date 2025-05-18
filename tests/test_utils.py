"""
Tests for the utils module
"""

from unittest.mock import patch

from djgpt.utils import debug, retry


class TestDebug:
    """Test debug function"""

    @patch("djgpt.utils.CONSOLE")
    @patch("djgpt.utils.LOGLEVEL", "DEBUG")
    def test_debug_logging_enabled(self, mock_console):
        """Test debug function when logging is enabled"""
        debug("Test message")
        mock_console.log.assert_called_once_with("Test message")

    @patch("djgpt.utils.CONSOLE")
    @patch("djgpt.utils.LOGLEVEL", "TRACE")
    def test_debug_trace_enabled(self, mock_console):
        """Test debug function when trace is enabled"""
        debug("Test message")
        mock_console.log.assert_called_once_with("Test message")

    @patch("djgpt.utils.CONSOLE")
    @patch("djgpt.utils.LOGLEVEL", "INFO")
    def test_debug_logging_disabled(self, mock_console):
        """Test debug function when logging is disabled"""
        debug("Test message")
        mock_console.log.assert_not_called()


class TestRetry:
    """Test retry decorator"""

    def test_retry_success_first_attempt(self):
        """Test retry when function succeeds on first attempt"""

        @retry
        def test_func():
            return "success"

        result = test_func()
        assert result == "success"

    def test_retry_success_after_failure(self):
        """Test retry when function succeeds after initially failing"""
        attempts = [0]  # Use list for mutable state

        @retry(num_attempts=3)
        def test_func():
            attempts[0] += 1
            if attempts[0] < 2:
                raise ValueError("Test error")
            return "success"

        result = test_func()
        assert result == "success"
        assert attempts[0] == 2  # Failed once, succeeded on second try

    def test_retry_all_attempts_fail(self):
        """Test retry when all attempts fail"""
        attempts = [0]

        @retry(num_attempts=3)
        def test_func():
            attempts[0] += 1
            raise ValueError("Test error")

        result = test_func()
        assert result is None
        assert attempts[0] == 3  # Failed three times

    def test_retry_none_is_fail(self):
        """Test retry with none_is_fail=True"""
        attempts = [0]

        @retry(none_is_fail=True, num_attempts=3)
        def test_func():
            attempts[0] += 1
            if attempts[0] < 2:
                return None
            return "success"

        result = test_func()
        assert result == "success"
        assert attempts[0] == 2  # None on first attempt, success on second

    @patch("time.sleep")
    def test_retry_with_sleep(self, mock_sleep):
        """Test retry with sleeptime"""
        attempts = [0]

        @retry(num_attempts=3, sleeptime=1)
        def test_func():
            attempts[0] += 1
            if attempts[0] < 2:
                raise ValueError("Test error")
            return "success"

        result = test_func()
        assert result == "success"
        mock_sleep.assert_called_once_with(1)

    @patch("time.sleep")
    def test_retry_with_cooloff(self, mock_sleep):
        """Test retry with cooloff"""
        attempts = [0]

        @retry(num_attempts=3, sleeptime=1, cooloff=True)
        def test_func():
            attempts[0] += 1
            if attempts[0] < 3:
                raise ValueError("Test error")
            return "success"

        result = test_func()
        assert result == "success"
        # First sleep should be 1 * 2 = 2 (attempt 2)
        # Second sleep should be 1 * 3 = 3 (attempt 3)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(2)
        mock_sleep.assert_any_call(3)

    def test_retry_specific_exception(self):
        """Test retry with specific exception class"""
        attempts = [0]

        @retry(exception_class=ValueError, num_attempts=3)
        def test_func():
            attempts[0] += 1
            if attempts[0] < 2:
                raise ValueError("Test error")
            return "success"

        result = test_func()
        assert result == "success"
        assert attempts[0] == 2
