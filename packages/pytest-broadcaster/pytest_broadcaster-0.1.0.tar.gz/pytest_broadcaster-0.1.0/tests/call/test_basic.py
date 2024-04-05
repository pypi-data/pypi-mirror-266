from __future__ import annotations

from pathlib import Path

import pytest
from pytest_broadcaster import __version__

from ._utils import CommonTestSetup


@pytest.mark.basic
class TestBasic(CommonTestSetup):
    """Scenario: A single test case within a single test file."""

    def test_omit_duration(self) -> None:
        data = {}
        assert self.omit_durations_and_times(data) == {}
        data = {"duration": 0.123}
        assert self.omit_durations_and_times(data) == {"duration": "omitted"}
        data = {"test": {"duration": 0.123}}
        assert self.omit_durations_and_times(data) == {"test": {"duration": "omitted"}}
        data = {"test": {"duration": 0.123, "nested": {"duration": 0.456}}}
        assert self.omit_durations_and_times(data) == {
            "test": {"duration": "omitted", "nested": {"duration": "omitted"}}
        }
        data = [{"duration": 0.123}, {"duration": 0.456}]
        assert self.omit_durations_and_times(data) == [
            {"duration": "omitted"},
            {"duration": "omitted"},
        ]
        data = [{"test": {"nested": [{"duration": 0.123}]}}]
        assert self.omit_durations_and_times(data) == [
            {"test": {"nested": [{"duration": "omitted"}]}}
        ]

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
        assert self.omit_durations_and_times(report) == {
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
                }
            ],
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
        assert self.omit_durations_and_times(lines) == [
            {
                "pytest_version": pytest.__version__,
                "plugin_version": __version__,
                "event": "SessionStart",
            },
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
                    },
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
            {"exit_status": 0, "event": "SessionFinish"},
        ]
