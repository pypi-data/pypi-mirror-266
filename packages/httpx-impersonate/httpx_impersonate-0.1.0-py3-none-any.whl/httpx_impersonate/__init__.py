from typing import Any

import httpx

from .ciphers import get_random_ssl_context
from .headers import get_random_headers

__version__ = "0.1.0"
__all__ = ["Client", "AsyncClient"]


class Client(httpx.Client):
    """httpx.Client with randomized headers and SSL context."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if "headers" not in kwargs:
            kwargs["headers"] = get_random_headers(http_version=2 if "http2" in kwargs else 1)
        if "verify" not in kwargs:
            kwargs["verify"] = get_random_ssl_context()
        super().__init__(
            *args,
            **kwargs,
        )


class AsyncClient(httpx.AsyncClient):
    """httpx.AsyncClient with randomized headers and SSL context."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if "headers" not in kwargs:
            kwargs["headers"] = get_random_headers(http_version=2 if "http2" in kwargs else 1)
        if "verify" not in kwargs:
            kwargs["verify"] = get_random_ssl_context()
        super().__init__(
            *args,
            **kwargs,
        )
