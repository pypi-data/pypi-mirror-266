from __future__ import annotations

import sys
from pathlib import Path

import pytest

from _testing.http_server import EmbeddedTestServer, Spy
from _testing.setup import CommonTestSetup
from pytest_broadcaster import __version__


class TestHttpDestination(CommonTestSetup):
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
        request = self.spy.expect_request()
        assert request.method() == "POST"
        assert request.path() == "/webhooks/TestWebhook"
        assert request.query_string() == ""
        assert self.sanitize(request.json()) == {
            "session_id": "omitted",
            "start_timestamp": "omitted",
            "stop_timestamp": "omitted",
            "project": None,
            "python": {
                "version": {
                    "major": sys.version_info.major,
                    "minor": sys.version_info.minor,
                    "micro": sys.version_info.micro,
                    "releaselevel": sys.version_info.releaselevel,
                },
                "platform": "omitted",
                "processor": "omitted",
                "packages": {},
            },
            "pytest_version": pytest.__version__,
            "plugin_version": __version__,
            "exit_status": 0,
            "errors": [],
            "warnings": [],
            "test_reports": [],
            "collect_reports": [
                {
                    "event": "collect_report",
                    "session_id": "omitted",
                    "node_id": "",
                    "timestamp": "omitted",
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
                    "event": "collect_report",
                    "session_id": "omitted",
                    "node_id": "test_basic.py",
                    "timestamp": "omitted",
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
                    "event": "collect_report",
                    "session_id": "omitted",
                    "node_id": ".",
                    "timestamp": "omitted",
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
        }
