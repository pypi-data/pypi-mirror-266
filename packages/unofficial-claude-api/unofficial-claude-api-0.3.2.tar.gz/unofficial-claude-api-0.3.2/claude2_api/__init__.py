"""Backward compatibility import (Before dev-0.3.1)"""
from claude_api.client import (
    ClaudeAPIClient,
    SendMessageResponse,
    HTTPProxy,
)
from claude_api.session import SessionData, get_session_data
from claude_api.errors import ClaudeAPIError, MessageRateLimitError, OverloadError


__all__ = [
    "ClaudeAPIClient",
    "SendMessageResponse",
    "HTTPProxy",
    "SessionData",
    "get_session_data",
    "MessageRateLimitError",
    "ClaudeAPIError",
    "OverloadError",
]
