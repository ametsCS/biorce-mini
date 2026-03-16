import logging
from unittest.mock import patch

from src.observability import (
    assert_langfuse_configured,
    assert_huggingface_token_configured,
)


def test_should_warn_when_langfuse_keys_are_missing(caplog):
    # Arrange
    env_without_keys = {"GEMINI_API_KEY": "fake"}

    # Act
    with patch("src.observability.load_dotenv"):  # Mock load_dotenv to avoid file I/O
        with patch.dict("os.environ", env_without_keys, clear=True):
            with caplog.at_level(logging.WARNING, logger="src.observability"):
                assert_langfuse_configured()

    # Assert
    actual = [r.message for r in caplog.records]
    assert len(caplog.records) > 0, (
        f"Expected log records but got none. Records: {caplog.records}"
    )
    assert any("Langfuse tracing disabled" in m for m in actual)


def test_should_not_warn_when_langfuse_keys_are_present(caplog):
    # Arrange
    env_with_keys = {
        "LANGFUSE_PUBLIC_KEY": "pk-lf-test",
        "LANGFUSE_SECRET_KEY": "sk-lf-test",
    }

    # Act
    with patch("src.observability.load_dotenv"):  # Mock load_dotenv to avoid file I/O
        with patch.dict("os.environ", env_with_keys, clear=True):
            with caplog.at_level(logging.WARNING, logger="src.observability"):
                assert_langfuse_configured()

    # Assert
    actual = [r.message for r in caplog.records]
    assert not any("Langfuse tracing disabled" in m for m in actual)


def test_should_warn_when_huggingface_token_is_missing(caplog):
    # Arrange
    env_without_token = {"GEMINI_API_KEY": "fake"}

    # Act
    with patch("src.observability.load_dotenv"):  # Mock load_dotenv to avoid file I/O
        with patch.dict("os.environ", env_without_token, clear=True):
            with caplog.at_level(logging.WARNING, logger="src.observability"):
                assert_huggingface_token_configured()

    # Assert
    actual = [r.message for r in caplog.records]
    assert any("HuggingFace token not configured" in m for m in actual)


def test_should_log_info_when_huggingface_token_is_present(caplog):
    # Arrange
    env_with_token = {"HF_TOKEN": "hf_test_token_12345"}

    # Act
    with patch("src.observability.load_dotenv"):  # Mock load_dotenv to avoid file I/O
        with patch.dict("os.environ", env_with_token, clear=True):
            with caplog.at_level(logging.INFO, logger="src.observability"):
                assert_huggingface_token_configured()

    # Assert
    actual = [r.message for r in caplog.records]
    assert any("HuggingFace token configured" in m for m in actual)
