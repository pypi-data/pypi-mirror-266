from __future__ import annotations

import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import flask
import pytest
from pytest_broadcaster import __version__
from werkzeug.serving import make_server


@dataclass
class SpyRequest:
    method: str
    path: str
    query: str
    json: Any


@dataclass
class Spy:
    received: list[SpyRequest] = field(default_factory=list)


class EmbeddedTestServer:
    def __init__(
        self,
        spy: Spy,
        path: str = "/webhooks/TestWebhook",
        host: str = "127.0.0.1",
        port: int = 8000,
    ) -> None:
        self.spy = spy
        self.thread = self.ServerThread(self.create_app(spy, path), host, port)

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.thread.shutdown()

    def __enter__(self) -> "EmbeddedTestServer":
        self.start()
        return self

    def __exit__(self, *args: object, **kwargs: object) -> None:
        self.stop()

    @staticmethod
    def create_app(spy: Spy, path: str):
        app = flask.Flask("test-app")

        @app.route(path, methods=["POST"])
        def webhook() -> dict[str, str]:
            spy.received.append(
                SpyRequest(
                    method=flask.request.method,
                    path=flask.request.path,
                    query=flask.request.query_string.decode(),
                    json=flask.request.get_json(),
                )
            )
            return {"status": "OK"}

        return app

    class ServerThread(threading.Thread):
        def __init__(self, app: flask.Flask, host: str, port: int):
            threading.Thread.__init__(self)
            self.server = make_server(host, port, app)
            self.ctx = app.app_context()
            self.ctx.push()

        def run(self):
            self.server.serve_forever()

        def shutdown(self):
            self.server.shutdown()


class TestHttpDestination:
    @pytest.fixture(autouse=True)
    def setup(
        self, pytester: pytest.Pytester, tmp_path: Path, pytestconfig: pytest.Config
    ):
        self.tmp_path = tmp_path
        self.test_dir = pytester
        self.pytestconfig = pytestconfig
        self.spy = Spy()
        with EmbeddedTestServer(
            self.spy,
            path="/webhooks/TestWebhook",
            host="127.0.0.1",
            port=8000,
        ) as server:
            yield server

    def make_testfile(self, filename: str, content: str) -> Path:
        if filename.endswith(".py"):
            filename = filename[:-3]
        else:
            raise ValueError("Filename must end with '.py'")
        kwargs = {filename: content}
        return self.test_dir.makepyfile(**kwargs)

    def make_test_directory(self) -> Path:
        self.test_dir.makeconftest("""
        from pytest_broadcaster import HTTPWebhook

        def pytest_broadcaster_add_destination(add):
            add(HTTPWebhook("http://localhost:8000/webhooks/TestWebhook"))
        """)
        return self.make_testfile(
            "test_basic.py",
            """
            '''This is a module docstring.'''

            def test_ok():
                '''This is a test docstring.'''
                pass
            """,
        ).parent

    def test_webhook(self):
        """Test HTTP webhook destination."""
        directory = self.make_test_directory()
        result = self.test_dir.runpytest("--collect-only")
        assert result.ret == 0
        assert self.spy.received == [
            SpyRequest(
                method="POST",
                path="/webhooks/TestWebhook",
                query="",
                json={
                    "pytest_version": pytest.__version__,
                    "plugin_version": __version__,
                    "exit_status": 0,
                    "errors": [],
                    "warnings": [],
                    "test_reports": [],
                    "collect_reports": [
                        {
                            "event": "CollectReport",
                            "node_id": "",
                            "items": [
                                {
                                    "node_id": ".",
                                    "node_type": "directory",
                                    "name": directory.name,
                                    "path": directory.name,
                                }
                            ],
                        },
                        {
                            "event": "CollectReport",
                            "node_id": "test_basic.py",
                            "items": [
                                {
                                    "node_id": "test_basic.py::test_ok",
                                    "node_type": "case",
                                    "name": "test_ok",
                                    "doc": "This is a test docstring.",
                                    "markers": [],
                                    "parameters": {},
                                    "path": directory.joinpath("test_basic.py")
                                    .relative_to(directory.parent)
                                    .as_posix(),
                                    "module": "test_basic",
                                    "suite": None,
                                    "function": "test_ok",
                                }
                            ],
                        },
                        {
                            "event": "CollectReport",
                            "node_id": ".",
                            "items": [
                                {
                                    "node_id": "test_basic.py",
                                    "name": "test_basic.py",
                                    "path": directory.joinpath("test_basic.py")
                                    .relative_to(directory.parent)
                                    .as_posix(),
                                    "doc": "This is a module docstring.",
                                    "markers": [],
                                    "node_type": "module",
                                }
                            ],
                        },
                    ],
                },
            ),
        ]
