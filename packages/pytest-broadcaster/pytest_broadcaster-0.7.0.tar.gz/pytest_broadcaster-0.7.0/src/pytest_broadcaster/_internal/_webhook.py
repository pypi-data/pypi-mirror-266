from __future__ import annotations

import http
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import urlparse

from ..interfaces import Destination
from ..models.session_event import SessionEvent
from ..models.session_result import SessionResult
from ._json_files import encode


class HTTPWebhook(Destination):
    def __init__(
        self,
        url: str,
        emit_events: bool = False,
        emit_result: bool = True,
        headers: dict[str, str] | None = None,
    ) -> None:
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        if not host:
            raise ValueError(f"Invalid webhook URL: {url}")
        self.url = url
        self.headers = headers or {}
        self.headers.setdefault("User-Agent", "pytest-broadcaster")
        self.parsed_url = parsed_url
        self.host = host
        self.emit_events = emit_events
        self.emit_result = emit_result
        self.uses_https = self.parsed_url.scheme == "https"
        if self.uses_https:
            self.headers.setdefault("Host", self.host)

    def write_event(self, event: SessionEvent) -> None:
        """Write an event to the destination."""
        if self.emit_events:
            self._post(encode(event))

    def write_result(self, result: SessionResult) -> None:
        """Write the session result to the destination."""
        if self.emit_result:
            self._post(encode(result))

    def summary(self) -> str | None:
        """Return a summary of the destination."""
        return f"Send report to HTTP webhook: {self.url}"

    def _post(self, data: str) -> None:
        if self.parsed_url.query:
            path_with_params = f"{self.parsed_url.path}?{self.parsed_url.query}"
        else:
            path_with_params = self.parsed_url.path
        if self.uses_https:
            connection = HTTPSConnection(host=self.host, port=self.parsed_url.port)
        else:
            connection = HTTPConnection(host=self.host, port=self.parsed_url.port)
        connection.request(
            method="POST",
            url=path_with_params,
            body=data,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(data)),
                **self.headers,
            },
        )
        response = connection.getresponse()
        if response.status != http.HTTPStatus.OK:
            raise RuntimeError(
                f"Failed to send webhook to {self.url}: {response.status} {response.reason}"
            )
