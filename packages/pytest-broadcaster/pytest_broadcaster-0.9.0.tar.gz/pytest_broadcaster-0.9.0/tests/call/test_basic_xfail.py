from __future__ import annotations

import sys
from pathlib import Path

import pytest

from _testing.setup import CommonTestSetup
from pytest_broadcaster import __version__


@pytest.mark.basic
class TestBasicxFail(CommonTestSetup):
    """Scenario: A single test case within a single test file which is marked with xfail."""

    def make_test_directory(self) -> Path:
        self.make_testfile(
            "test_basic.py",
            """
            '''This is a module docstring.'''

            def test_ok():
                '''This is a test docstring.'''
                pass
            """,
        )
        return self.make_testfile(
            "test_basic_xfail.py",
            """
            '''This is a module docstring.'''
            import pytest

            @pytest.mark.xfail(raises=ValueError)
            def test_xfail():
                '''This is a test docstring.'''
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
                },
                {
                    "node_id": "test_basic_xfail.py::test_xfail",
                    "outcome": "xfailed",
                    "duration": "omitted",
                    "setup": {
                        "event": "case_setup",
                        "session_id": "omitted",
                        "node_id": "test_basic_xfail.py::test_xfail",
                        "outcome": "passed",
                        "duration": "omitted",
                        "start_timestamp": "omitted",
                        "stop_timestamp": "omitted",
                        "error": None,
                    },
                    "call": {
                        "event": "case_call",
                        "session_id": "omitted",
                        "node_id": "test_basic_xfail.py::test_xfail",
                        "outcome": "xfailed",
                        "duration": "omitted",
                        "start_timestamp": "omitted",
                        "stop_timestamp": "omitted",
                        "error": None,
                    },
                    "teardown": {
                        "event": "case_teardown",
                        "session_id": "omitted",
                        "node_id": "test_basic_xfail.py::test_xfail",
                        "outcome": "passed",
                        "duration": "omitted",
                        "start_timestamp": "omitted",
                        "stop_timestamp": "omitted",
                        "error": None,
                    },
                    "finished": {
                        "event": "case_finished",
                        "session_id": "omitted",
                        "node_id": "test_basic_xfail.py::test_xfail",
                        "outcome": "xfailed",
                        "total_duration": "omitted",
                        "start_timestamp": "omitted",
                        "stop_timestamp": "omitted",
                    },
                },
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
                    "node_id": "test_basic_xfail.py",
                    "timestamp": "omitted",
                    "items": [
                        {
                            "node_id": "test_basic_xfail.py::test_xfail",
                            "node_type": "case",
                            "name": "test_xfail",
                            "doc": "This is a test docstring.",
                            "markers": ["xfail"],
                            "parameters": {},
                            "path": directory.joinpath("test_basic_xfail.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_basic_xfail",
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
                            "node_id": "test_basic.py",
                            "name": "test_basic.py",
                            "path": directory.joinpath("test_basic.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "doc": "This is a module docstring.",
                            "markers": [],
                            "node_type": "module",
                        },
                        {
                            "node_id": "test_basic_xfail.py",
                            "name": "test_basic_xfail.py",
                            "path": directory.joinpath("test_basic_xfail.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "doc": "This is a module docstring.",
                            "markers": [],
                            "node_type": "module",
                        },
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
                    }
                ],
            },
            {
                "event": "collect_report",
                "session_id": "omitted",
                "node_id": "test_basic_xfail.py",
                "timestamp": "omitted",
                "items": [
                    {
                        "node_id": "test_basic_xfail.py::test_xfail",
                        "node_type": "case",
                        "name": "test_xfail",
                        "doc": "This is a test docstring.",
                        "markers": ["xfail"],
                        "parameters": {},
                        "path": directory.joinpath("test_basic_xfail.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_basic_xfail",
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
                        "node_id": "test_basic.py",
                        "name": "test_basic.py",
                        "path": directory.joinpath("test_basic.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "doc": "This is a module docstring.",
                        "markers": [],
                        "node_type": "module",
                    },
                    {
                        "node_id": "test_basic_xfail.py",
                        "name": "test_basic_xfail.py",
                        "path": directory.joinpath("test_basic_xfail.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "doc": "This is a module docstring.",
                        "markers": [],
                        "node_type": "module",
                    },
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
                "event": "case_setup",
                "session_id": "omitted",
                "node_id": "test_basic_xfail.py::test_xfail",
                "outcome": "passed",
                "duration": "omitted",
                "start_timestamp": "omitted",
                "stop_timestamp": "omitted",
                "error": None,
            },
            {
                "event": "case_call",
                "session_id": "omitted",
                "node_id": "test_basic_xfail.py::test_xfail",
                "outcome": "xfailed",
                "duration": "omitted",
                "start_timestamp": "omitted",
                "stop_timestamp": "omitted",
                "error": None,
            },
            {
                "event": "case_teardown",
                "session_id": "omitted",
                "node_id": "test_basic_xfail.py::test_xfail",
                "outcome": "passed",
                "duration": "omitted",
                "start_timestamp": "omitted",
                "stop_timestamp": "omitted",
                "error": None,
            },
            {
                "event": "case_finished",
                "session_id": "omitted",
                "node_id": "test_basic_xfail.py::test_xfail",
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
