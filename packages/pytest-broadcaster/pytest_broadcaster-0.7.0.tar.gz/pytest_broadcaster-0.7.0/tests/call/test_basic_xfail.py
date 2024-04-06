from __future__ import annotations

from pathlib import Path

import pytest

from pytest_broadcaster import __version__

from ._utils import CommonTestSetup


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
        assert self.omit_durations_and_times(self.read_json_file()) == {
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
                        "event_type": "case_setup",
                        "node_id": "test_basic.py::test_ok",
                        "outcome": "passed",
                        "duration": "omitted",
                        "start": "omitted",
                        "stop": "omitted",
                        "error": None,
                    },
                    "call": {
                        "event_type": "case_call",
                        "node_id": "test_basic.py::test_ok",
                        "outcome": "passed",
                        "duration": "omitted",
                        "start": "omitted",
                        "stop": "omitted",
                        "error": None,
                    },
                    "teardown": {
                        "event_type": "case_teardown",
                        "node_id": "test_basic.py::test_ok",
                        "outcome": "passed",
                        "duration": "omitted",
                        "start": "omitted",
                        "stop": "omitted",
                        "error": None,
                    },
                    "finished": {
                        "event_type": "case_finished",
                        "node_id": "test_basic.py::test_ok",
                        "outcome": "passed",
                        "duration": "omitted",
                        "start": "omitted",
                        "stop": "omitted",
                    },
                },
                {
                    "node_id": "test_basic_xfail.py::test_xfail",
                    "outcome": "xfailed",
                    "duration": "omitted",
                    "setup": {
                        "event_type": "case_setup",
                        "node_id": "test_basic_xfail.py::test_xfail",
                        "outcome": "passed",
                        "duration": "omitted",
                        "start": "omitted",
                        "stop": "omitted",
                        "error": None,
                    },
                    "call": {
                        "event_type": "case_call",
                        "node_id": "test_basic_xfail.py::test_xfail",
                        "outcome": "xfailed",
                        "duration": "omitted",
                        "start": "omitted",
                        "stop": "omitted",
                        "error": None,
                    },
                    "teardown": {
                        "event_type": "case_teardown",
                        "node_id": "test_basic_xfail.py::test_xfail",
                        "outcome": "passed",
                        "duration": "omitted",
                        "start": "omitted",
                        "stop": "omitted",
                        "error": None,
                    },
                    "finished": {
                        "event_type": "case_finished",
                        "node_id": "test_basic_xfail.py::test_xfail",
                        "outcome": "xfailed",
                        "duration": "omitted",
                        "start": "omitted",
                        "stop": "omitted",
                    },
                },
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
                    "event": "collect_report",
                    "node_id": "test_basic_xfail.py",
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
                "event": "collect_report",
                "node_id": "test_basic_xfail.py",
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
                "event_type": "case_setup",
                "node_id": "test_basic.py::test_ok",
                "outcome": "passed",
                "duration": "omitted",
                "start": "omitted",
                "stop": "omitted",
                "error": None,
            },
            {
                "event_type": "case_call",
                "node_id": "test_basic.py::test_ok",
                "outcome": "passed",
                "duration": "omitted",
                "start": "omitted",
                "stop": "omitted",
                "error": None,
            },
            {
                "event_type": "case_teardown",
                "node_id": "test_basic.py::test_ok",
                "outcome": "passed",
                "duration": "omitted",
                "start": "omitted",
                "stop": "omitted",
                "error": None,
            },
            {
                "event_type": "case_finished",
                "node_id": "test_basic.py::test_ok",
                "outcome": "passed",
                "duration": "omitted",
                "start": "omitted",
                "stop": "omitted",
            },
            {
                "event_type": "case_setup",
                "node_id": "test_basic_xfail.py::test_xfail",
                "outcome": "passed",
                "duration": "omitted",
                "start": "omitted",
                "stop": "omitted",
                "error": None,
            },
            {
                "event_type": "case_call",
                "node_id": "test_basic_xfail.py::test_xfail",
                "outcome": "xfailed",
                "duration": "omitted",
                "start": "omitted",
                "stop": "omitted",
                "error": None,
            },
            {
                "event_type": "case_teardown",
                "node_id": "test_basic_xfail.py::test_xfail",
                "outcome": "passed",
                "duration": "omitted",
                "start": "omitted",
                "stop": "omitted",
                "error": None,
            },
            {
                "event_type": "case_finished",
                "node_id": "test_basic_xfail.py::test_xfail",
                "outcome": "xfailed",
                "duration": "omitted",
                "start": "omitted",
                "stop": "omitted",
            },
            {"exit_status": 0, "event": "session_finish"},
        ]
