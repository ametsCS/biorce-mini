# src/observability.py
import logging
import os

from dotenv import load_dotenv
from langfuse import Langfuse, observe

logger = logging.getLogger(__name__)

_REQUIRED_ENV_VARS = ["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]


def get_langfuse() -> Langfuse:
    from langfuse import get_client

    return get_client()


def assert_langfuse_configured() -> None:
    load_dotenv()
    missing = [k for k in _REQUIRED_ENV_VARS if not os.getenv(k)]
    if missing:
        logger.warning("Langfuse tracing disabled. missing_keys=%s", missing)
