from __future__ import annotations

import sys
from pathlib import Path

import pytest

from _testing.setup import CommonTestSetup
from pytest_broadcaster import __version__


@pytest.mark.basic
class TestBasicFailure(CommonTestSetup):
    """Scenario: A single test case within a single test file which fails."""

    def make_test_directory(self) -> Path:
        return self.make_testfile(
            "test_basic_failure.py",
            """
            '''This is a module docstring.'''

            def test_failure():
                '''This is a test docstring.'''
                raise ValueError("BOOM")
            """,
        ).parent

    def test_json(self):
        """Test JSON report for single test case within single test file."""

        directory = self.make_test_directory()
        result = self.test_dir.runpytest("--collect-report", self.json_file.as_posix())
        assert result.ret == 1
        assert self.json_file.exists()
        assert self.sanitize(self.read_json_file()) == {
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
            "exit_status": 1,
            "errors": [],
            "warnings": [],
            "test_reports": [
                {
                    "node_id": "test_basic_failure.py::test_failure",
                    "outcome": "failed",
                    "duration": "omitted",
                    "setup": {
                        "event": "case_setup",
                        "session_id": "omitted",
                        "node_id": "test_basic_failure.py::test_failure",
                        "outcome": "passed",
                        "duration": "omitted",
                        "start_timestamp": "omitted",
                        "stop_timestamp": "omitted",
                        "error": None,
                    },
                    "call": {
                        "event": "case_call",
                        "session_id": "omitted",
                        "node_id": "test_basic_failure.py::test_failure",
                        "outcome": "failed",
                        "duration": "omitted",
                        "start_timestamp": "omitted",
                        "stop_timestamp": "omitted",
                        "error": {
                            "message": "def test_failure():\n        '''This is a test docstring.'''\n>       raise ValueError(\"BOOM\")\nE       ValueError: BOOM\n\ntest_basic_failure.py:5: ValueError",
                            "traceback": {
                                "entries": [
                                    {
                                        "path": "test_basic_failure.py",
                                        "lineno": 5,
                                        "message": "ValueError",
                                    }
                                ]
                            },
                        },
                    },
                    "teardown": {
                        "event": "case_teardown",
                        "session_id": "omitted",
                        "node_id": "test_basic_failure.py::test_failure",
                        "outcome": "passed",
                        "duration": "omitted",
                        "start_timestamp": "omitted",
                        "stop_timestamp": "omitted",
                        "error": None,
                    },
                    "finished": {
                        "event": "case_finished",
                        "session_id": "omitted",
                        "node_id": "test_basic_failure.py::test_failure",
                        "outcome": "failed",
                        "start_timestamp": "omitted",
                        "stop_timestamp": "omitted",
                        "total_duration": "omitted",
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
                    "node_id": "test_basic_failure.py",
                    "timestamp": "omitted",
                    "items": [
                        {
                            "node_id": "test_basic_failure.py::test_failure",
                            "node_type": "case",
                            "name": "test_failure",
                            "doc": "This is a test docstring.",
                            "markers": [],
                            "parameters": {},
                            "path": directory.joinpath("test_basic_failure.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_basic_failure",
                            "suite": None,
                            "function": "test_failure",
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
                            "node_id": "test_basic_failure.py",
                            "name": "test_basic_failure.py",
                            "path": directory.joinpath("test_basic_failure.py")
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

    def test_jsonl_basic(self):
        """Test JSON Lines report for single test case within single test file."""

        directory = self.make_test_directory()
        result = self.test_dir.runpytest(
            "--collect-log", self.json_lines_file.as_posix()
        )
        assert result.ret == 1
        assert self.json_lines_file.exists()
        assert self.sanitize(self.read_json_lines_file()) == [
            {
                "event": "session_start",
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
                "node_id": "test_basic_failure.py",
                "timestamp": "omitted",
                "items": [
                    {
                        "node_id": "test_basic_failure.py::test_failure",
                        "node_type": "case",
                        "name": "test_failure",
                        "doc": "This is a test docstring.",
                        "markers": [],
                        "parameters": {},
                        "path": directory.joinpath("test_basic_failure.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_basic_failure",
                        "suite": None,
                        "function": "test_failure",
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
                        "node_id": "test_basic_failure.py",
                        "name": "test_basic_failure.py",
                        "path": directory.joinpath("test_basic_failure.py")
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
                "node_id": "test_basic_failure.py::test_failure",
                "outcome": "passed",
                "duration": "omitted",
                "start_timestamp": "omitted",
                "stop_timestamp": "omitted",
                "error": None,
            },
            {
                "event": "case_call",
                "session_id": "omitted",
                "node_id": "test_basic_failure.py::test_failure",
                "outcome": "failed",
                "duration": "omitted",
                "start_timestamp": "omitted",
                "stop_timestamp": "omitted",
                "error": {
                    "message": "def test_failure():\n        '''This is a test docstring.'''\n>       raise ValueError(\"BOOM\")\nE       ValueError: BOOM\n\ntest_basic_failure.py:5: ValueError",
                    "traceback": {
                        "entries": [
                            {
                                "path": "test_basic_failure.py",
                                "lineno": 5,
                                "message": "ValueError",
                            }
                        ]
                    },
                },
            },
            {
                "event": "case_teardown",
                "session_id": "omitted",
                "node_id": "test_basic_failure.py::test_failure",
                "outcome": "passed",
                "duration": "omitted",
                "start_timestamp": "omitted",
                "stop_timestamp": "omitted",
                "error": None,
            },
            {
                "event": "case_finished",
                "session_id": "omitted",
                "node_id": "test_basic_failure.py::test_failure",
                "outcome": "failed",
                "total_duration": "omitted",
                "start_timestamp": "omitted",
                "stop_timestamp": "omitted",
            },
            {
                "exit_status": 1,
                "event": "session_finish",
                "session_id": "omitted",
                "timestamp": "omitted",
            },
        ]
