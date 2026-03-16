import logging
from unittest.mock import patch

from src.observability import assert_langfuse_configured


def test_should_warn_when_langfuse_keys_are_missing(caplog):
    # Arrange
    env_without_keys = {"GEMINI_API_KEY": "fake"}

    # Act
    with patch.dict("os.environ", env_without_keys, clear=True):
        with caplog.at_level(logging.WARNING, logger="src.observability"):
            assert_langfuse_configured()

    # Assert
    actual = [r.message for r in caplog.records]
    assert any("Langfuse tracing disabled" in m for m in actual)


def test_should_not_warn_when_langfuse_keys_are_present(caplog):
    # Arrange
    env_with_keys = {
        "LANGFUSE_PUBLIC_KEY": "pk-lf-test",
        "LANGFUSE_SECRET_KEY": "sk-lf-test",
    }

    # Act
    with patch.dict("os.environ", env_with_keys, clear=True):
        with caplog.at_level(logging.WARNING, logger="src.observability"):
            assert_langfuse_configured()

    # Assert
    actual = [r.message for r in caplog.records]
    assert not any("Langfuse tracing disabled" in m for m in actual)
