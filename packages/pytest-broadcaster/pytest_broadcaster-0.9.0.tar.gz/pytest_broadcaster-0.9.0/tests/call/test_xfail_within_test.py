from __future__ import annotations

import sys
from pathlib import Path

import pytest

from _testing.setup import CommonTestSetup
from pytest_broadcaster import __version__


@pytest.mark.basic
class TestxFailWithinTest(CommonTestSetup):
    """Scenario: A single test case within a single test file which calls xfail() during execution."""

    def make_test_directory(self) -> Path:
        return self.make_testfile(
            "test_xfail_within_test.py",
            """
            '''This is a module docstring.'''
            import pytest

            def test_xfail():
                '''This is a test docstring.'''
                pytest.xfail("failing configuration (but should work)")
                raise ValueError("BOOM")
            """,
        ).parent

    def test_json(self):
        """Test JSON report for single test case within single test file."""

        directory = self.make_test_directory()
        result = self.test_dir.runpytest("--collect-report", self.json_file.as_posix())
        assert result.ret == 0
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
            "exit_status": 0,
            "errors": [],
            "warnings": [],
            "test_reports": [
                {
                    "node_id": "test_xfail_within_test.py::test_xfail",
                    "outcome": "xfailed",
                    "duration": "omitted",
                    "setup": {
                        "event": "case_setup",
                        "session_id": "omitted",
                        "node_id": "test_xfail_within_test.py::test_xfail",
                        "outcome": "passed",
                        "duration": "omitted",
                        "start_timestamp": "omitted",
                        "stop_timestamp": "omitted",
                        "error": None,
                    },
                    "call": {
                        "event": "case_call",
                        "session_id": "omitted",
                        "node_id": "test_xfail_within_test.py::test_xfail",
                        "outcome": "xfailed",
                        "duration": "omitted",
                        "start_timestamp": "omitted",
                        "stop_timestamp": "omitted",
                        "error": None,
                    },
                    "teardown": {
                        "event": "case_teardown",
                        "session_id": "omitted",
                        "node_id": "test_xfail_within_test.py::test_xfail",
                        "outcome": "passed",
                        "duration": "omitted",
                        "start_timestamp": "omitted",
                        "stop_timestamp": "omitted",
                        "error": None,
                    },
                    "finished": {
                        "event": "case_finished",
                        "session_id": "omitted",
                        "node_id": "test_xfail_within_test.py::test_xfail",
                        "outcome": "xfailed",
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
                    "node_id": "test_xfail_within_test.py",
                    "timestamp": "omitted",
                    "items": [
                        {
                            "node_id": "test_xfail_within_test.py::test_xfail",
                            "node_type": "case",
                            "name": "test_xfail",
                            "doc": "This is a test docstring.",
                            "markers": [],
                            "parameters": {},
                            "path": directory.joinpath("test_xfail_within_test.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_xfail_within_test",
                            "suite": None,
                            "function": "test_xfail",
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
                            "node_id": "test_xfail_within_test.py",
                            "name": "test_xfail_within_test.py",
                            "path": directory.joinpath("test_xfail_within_test.py")
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

    def test_jsonl(self):
        """Test JSON Lines report for single test case within single test file."""

        directory = self.make_test_directory()
        result = self.test_dir.runpytest(
            "--collect-log", self.json_lines_file.as_posix()
        )
        assert result.ret == 0
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
                "node_id": "test_xfail_within_test.py",
                "timestamp": "omitted",
                "items": [
                    {
                        "node_id": "test_xfail_within_test.py::test_xfail",
                        "node_type": "case",
                        "name": "test_xfail",
                        "doc": "This is a test docstring.",
                        "markers": [],
                        "parameters": {},
                        "path": directory.joinpath("test_xfail_within_test.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_xfail_within_test",
                        "suite": None,
                        "function": "test_xfail",
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
                        "node_id": "test_xfail_within_test.py",
                        "name": "test_xfail_within_test.py",
                        "path": directory.joinpath("test_xfail_within_test.py")
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
                "node_id": "test_xfail_within_test.py::test_xfail",
                "outcome": "passed",
                "duration": "omitted",
                "start_timestamp": "omitted",
                "stop_timestamp": "omitted",
                "error": None,
            },
            {
                "event": "case_call",
                "session_id": "omitted",
                "node_id": "test_xfail_within_test.py::test_xfail",
                "outcome": "xfailed",
                "duration": "omitted",
                "start_timestamp": "omitted",
                "stop_timestamp": "omitted",
                "error": None,
            },
            {
                "event": "case_teardown",
                "session_id": "omitted",
                "node_id": "test_xfail_within_test.py::test_xfail",
                "outcome": "passed",
                "duration": "omitted",
                "start_timestamp": "omitted",
                "stop_timestamp": "omitted",
                "error": None,
            },
            {
                "event": "case_finished",
                "session_id": "omitted",
                "node_id": "test_xfail_within_test.py::test_xfail",
                "outcome": "xfailed",
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
