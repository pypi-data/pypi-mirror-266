from typing import TYPE_CHECKING

from starlette.datastructures import MutableHeaders
from asgi_correlation_id import CorrelationIdMiddleware as ASGICorrelationIdMiddleware

from kilmlogger.constants import CORRELATION_HEADER


if TYPE_CHECKING:
    from starlette.types import Receive, Scope, Send


class CorrelationIdMiddleware(ASGICorrelationIdMiddleware):
    header_name: str = CORRELATION_HEADER
    is_required_header: bool = True

    def __init__(self, app, **kwargs):
        if "header_name" in kwargs:
            self.header_name = kwargs.pop("header_name")
        if "is_required_header" in kwargs:
            self.is_required_header = kwargs.pop("is_required_header")

        super().__init__(app, header_name=self.header_name, **kwargs)

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        Check header
        """
        # Try to load correlation ID from the request headers
        headers = MutableHeaders(scope=scope)
        header_value = headers.get(self.header_name.lower())
        if not header_value and self.is_required_header:
            raise ValueError(f"Missing {self.header_name} header")

        return await super().__call__(scope, receive, send)
