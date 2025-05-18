"""Simple CI tests for DJGPT"""

from unittest import mock

import pytest


def test_djgpt_dummy():
    """Test that our CI pipeline can run a simple test"""
    assert True


@pytest.mark.skip(reason="Only for CI demonstration purposes")
def test_mock_openai_api():
    """Test that we can mock the OpenAI API"""
    with mock.patch("openai.ChatCompletion.create") as mocked_create:
        # Configure the mock to return a fixed response
        mocked_create.return_value = {
            "choices": [
                {"message": {"content": '[{"artist": "Mock Artist", "trackname": "Mock Song"}]'}}
            ]
        }

        # Access the mocked API
        import openai

        response = openai.ChatCompletion.create(
            model="gpt-4", messages=[{"role": "user", "content": "Recommend music"}]
        )

        # Verify we get the expected response
        assert (
            response["choices"][0]["message"]["content"]
            == '[{"artist": "Mock Artist", "trackname": "Mock Song"}]'
        )
