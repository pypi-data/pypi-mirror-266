from __future__ import annotations

from pathlib import Path

import pytest

from pytest_broadcaster import __version__

from ._utils import CommonTestSetup


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
        assert self.omit_durations_and_times(self.read_json_file()) == {
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
                        "event_type": "case_setup",
                        "node_id": "test_basic_failure.py::test_failure",
                        "outcome": "passed",
                        "duration": "omitted",
                        "start": "omitted",
                        "stop": "omitted",
                        "error": None,
                    },
                    "call": {
                        "event_type": "case_call",
                        "node_id": "test_basic_failure.py::test_failure",
                        "outcome": "failed",
                        "duration": "omitted",
                        "start": "omitted",
                        "stop": "omitted",
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
                        "event_type": "case_teardown",
                        "node_id": "test_basic_failure.py::test_failure",
                        "outcome": "passed",
                        "duration": "omitted",
                        "start": "omitted",
                        "stop": "omitted",
                        "error": None,
                    },
                    "finished": {
                        "event_type": "case_finished",
                        "node_id": "test_basic_failure.py::test_failure",
                        "outcome": "failed",
                        "duration": "omitted",
                        "start": "omitted",
                        "stop": "omitted",
                    },
                }
            ],
            "collect_reports": [
                {
                    "event": "collect_report",
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
                    "event": "collect_report",
                    "node_id": "test_basic_failure.py",
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
                    "node_id": ".",
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
        assert self.omit_durations_and_times(self.read_json_lines_file()) == [
            {
                "pytest_version": pytest.__version__,
                "plugin_version": __version__,
                "event": "session_start",
            },
            {
                "event": "collect_report",
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
                "event": "collect_report",
                "node_id": "test_basic_failure.py",
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
                "node_id": ".",
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
                "event_type": "case_setup",
                "node_id": "test_basic_failure.py::test_failure",
                "outcome": "passed",
                "duration": "omitted",
                "start": "omitted",
                "stop": "omitted",
                "error": None,
            },
            {
                "event_type": "case_call",
                "node_id": "test_basic_failure.py::test_failure",
                "outcome": "failed",
                "duration": "omitted",
                "start": "omitted",
                "stop": "omitted",
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
                "event_type": "case_teardown",
                "node_id": "test_basic_failure.py::test_failure",
                "outcome": "passed",
                "duration": "omitted",
                "start": "omitted",
                "stop": "omitted",
                "error": None,
            },
            {
                "event_type": "case_finished",
                "node_id": "test_basic_failure.py::test_failure",
                "outcome": "failed",
                "duration": "omitted",
                "start": "omitted",
                "stop": "omitted",
            },
            {"exit_status": 1, "event": "session_finish"},
        ]
