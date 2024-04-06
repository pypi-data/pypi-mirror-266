from __future__ import annotations

import sys
from pathlib import Path

import pytest

from _testing.setup import CommonTestSetup
from pytest_broadcaster import __version__


@pytest.mark.basic
class TestBasic(CommonTestSetup):
    """Scenario: A single test case within a single test file."""

    def test_omit_duration(self) -> None:
        data = {}
        assert self.sanitize(data) == {}
        data = {"duration": 0.123}
        assert self.sanitize(data) == {"duration": "omitted"}
        data = {"test": {"duration": 0.123}}
        assert self.sanitize(data) == {"test": {"duration": "omitted"}}
        data = {"test": {"duration": 0.123, "nested": {"duration": 0.456}}}
        assert self.sanitize(data) == {
            "test": {"duration": "omitted", "nested": {"duration": "omitted"}}
        }
        data = [{"duration": 0.123}, {"duration": 0.456}]
        assert self.sanitize(data) == [
            {"duration": "omitted"},
            {"duration": "omitted"},
        ]
        data = [{"test": {"nested": [{"duration": 0.123}]}}]
        assert self.sanitize(data) == [{"test": {"nested": [{"duration": "omitted"}]}}]

    def make_test_directory(self) -> Path:
        return self.make_testfile(
            "test_basic.py",
            """
            '''This is a module docstring.'''

            def test_ok():
                '''This is a test docstring.'''
                pass
            """,
        ).parent

    def test_json(self):
        """Test JSON report for single test case within single test file."""

        directory = self.make_test_directory()
        result = self.test_dir.runpytest("--collect-report", self.json_file.as_posix())
        assert result.ret == 0
        assert self.json_file.exists()
        report = self.read_json_file()
        assert self.sanitize(report) == {
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
            "test_reports": [
                {
                    "node_id": "test_basic.py::test_ok",
                    "outcome": "passed",
                    "duration": "omitted",
                    "setup": {
                        "event": "case_setup",
                        "session_id": "omitted",
                        "node_id": "test_basic.py::test_ok",
                        "outcome": "passed",
                        "duration": "omitted",
                        "start_timestamp": "omitted",
                        "stop_timestamp": "omitted",
                        "error": None,
                    },
                    "call": {
                        "event": "case_call",
                        "session_id": "omitted",
                        "node_id": "test_basic.py::test_ok",
                        "outcome": "passed",
                        "duration": "omitted",
                        "start_timestamp": "omitted",
                        "stop_timestamp": "omitted",
                        "error": None,
                    },
                    "teardown": {
                        "event": "case_teardown",
                        "session_id": "omitted",
                        "node_id": "test_basic.py::test_ok",
                        "outcome": "passed",
                        "duration": "omitted",
                        "start_timestamp": "omitted",
                        "stop_timestamp": "omitted",
                        "error": None,
                    },
                    "finished": {
                        "event": "case_finished",
                        "session_id": "omitted",
                        "node_id": "test_basic.py::test_ok",
                        "outcome": "passed",
                        "total_duration": "omitted",
                        "start_timestamp": "omitted",
                        "stop_timestamp": "omitted",
                    },
                }
            ],
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
        assert report["test_reports"][0]["duration"] == (
            report["test_reports"][0]["setup"]["duration"]
            + report["test_reports"][0]["call"]["duration"]
            + report["test_reports"][0]["teardown"]["duration"]
        )

    def test_jsonl_basic(self):
        """Test JSON Lines report for single test case within single test file."""

        directory = self.make_test_directory()
        result = self.test_dir.runpytest(
            "--collect-log", self.json_lines_file.as_posix()
        )
        assert result.ret == 0
        assert self.json_lines_file.exists()
        lines = self.read_json_lines_file()
        assert self.sanitize(lines) == [
            {
                "session_id": "omitted",
                "timestamp": "omitted",
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
                "event": "session_start",
            },
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
                    },
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
            {
                "event": "case_setup",
                "session_id": "omitted",
                "node_id": "test_basic.py::test_ok",
                "outcome": "passed",
                "duration": "omitted",
                "start_timestamp": "omitted",
                "stop_timestamp": "omitted",
                "error": None,
            },
            {
                "event": "case_call",
                "session_id": "omitted",
                "node_id": "test_basic.py::test_ok",
                "outcome": "passed",
                "duration": "omitted",
                "start_timestamp": "omitted",
                "stop_timestamp": "omitted",
                "error": None,
            },
            {
                "event": "case_teardown",
                "session_id": "omitted",
                "node_id": "test_basic.py::test_ok",
                "outcome": "passed",
                "duration": "omitted",
                "start_timestamp": "omitted",
                "stop_timestamp": "omitted",
                "error": None,
            },
            {
                "event": "case_finished",
                "session_id": "omitted",
                "node_id": "test_basic.py::test_ok",
                "outcome": "passed",
                "total_duration": "omitted",
                "start_timestamp": "omitted",
                "stop_timestamp": "omitted",
            },
            {
                "exit_status": 0,
                "event": "session_finish",
                "session_id": "omitted",
                "timestamp": "omitted",
            },
        ]
