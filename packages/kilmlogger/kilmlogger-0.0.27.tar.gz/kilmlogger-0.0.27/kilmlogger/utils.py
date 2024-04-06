import logging

from typing import Any

from asgi_correlation_id import correlation_id

from kilmlogger.constants import CORRELATION_KEY


def add_correlation(
    logger: logging.Logger, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add request id to log message."""
    if request_id := correlation_id.get():
        event_dict[CORRELATION_KEY] = request_id
    return event_dict
