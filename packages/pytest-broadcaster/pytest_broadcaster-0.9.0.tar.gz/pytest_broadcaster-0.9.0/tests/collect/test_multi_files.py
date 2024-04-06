from __future__ import annotations

import sys
from pathlib import Path

import pytest

from _testing.setup import CommonTestSetup
from pytest_broadcaster import __version__


@pytest.mark.basic
@pytest.mark.filetree
class TestMultiFiles(CommonTestSetup):
    """Scenario: several test files with several test cases."""

    def make_test_directory(self) -> Path:
        self.make_testfile(
            "test_module_1.py",
            """
            def test_1():
                '''This is a test docstring.'''
                pass

            def test_2():
                '''This is a test docstring.'''
                pass
            """,
        )
        return self.make_testfile(
            "test_module_2.py",
            """
            def test_3():
                '''This is a test docstring.'''
                pass

            def test_4():
                '''This is a test docstring.'''
                pass
            """,
        ).parent

    def test_json(self):
        """Test JSON report for several test cases within several test files."""

        directory = self.make_test_directory()
        result = self.test_dir.runpytest(
            "--collect-only", "--collect-report", self.json_file.as_posix()
        )
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
                    "node_id": "test_module_1.py",
                    "timestamp": "omitted",
                    "items": [
                        {
                            "node_id": "test_module_1.py::test_1",
                            "node_type": "case",
                            "name": "test_1",
                            "doc": "This is a test docstring.",
                            "markers": [],
                            "parameters": {},
                            "path": directory.joinpath("test_module_1.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_module_1",
                            "suite": None,
                            "function": "test_1",
                        },
                        {
                            "node_id": "test_module_1.py::test_2",
                            "node_type": "case",
                            "name": "test_2",
                            "doc": "This is a test docstring.",
                            "markers": [],
                            "parameters": {},
                            "path": directory.joinpath("test_module_1.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_module_1",
                            "suite": None,
                            "function": "test_2",
                        },
                    ],
                },
                {
                    "event": "collect_report",
                    "session_id": "omitted",
                    "node_id": "test_module_2.py",
                    "timestamp": "omitted",
                    "items": [
                        {
                            "node_id": "test_module_2.py::test_3",
                            "node_type": "case",
                            "name": "test_3",
                            "doc": "This is a test docstring.",
                            "markers": [],
                            "parameters": {},
                            "path": directory.joinpath("test_module_2.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_module_2",
                            "suite": None,
                            "function": "test_3",
                        },
                        {
                            "node_id": "test_module_2.py::test_4",
                            "node_type": "case",
                            "name": "test_4",
                            "doc": "This is a test docstring.",
                            "markers": [],
                            "parameters": {},
                            "path": directory.joinpath("test_module_2.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_module_2",
                            "suite": None,
                            "function": "test_4",
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
                            "node_id": "test_module_1.py",
                            "node_type": "module",
                            "name": "test_module_1.py",
                            "path": directory.joinpath("test_module_1.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "doc": "",
                            "markers": [],
                        },
                        {
                            "node_id": "test_module_2.py",
                            "node_type": "module",
                            "name": "test_module_2.py",
                            "path": directory.joinpath("test_module_2.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "doc": "",
                            "markers": [],
                        },
                    ],
                },
            ],
        }

    def test_jsonl(self):
        """Test JSON Lines report for several test cases within several test files."""

        directory = self.make_test_directory()
        result = self.test_dir.runpytest(
            "--collect-only", "--collect-log", self.json_lines_file.as_posix()
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
                "node_id": "test_module_1.py",
                "timestamp": "omitted",
                "items": [
                    {
                        "node_id": "test_module_1.py::test_1",
                        "node_type": "case",
                        "name": "test_1",
                        "doc": "This is a test docstring.",
                        "markers": [],
                        "parameters": {},
                        "path": directory.joinpath("test_module_1.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_module_1",
                        "suite": None,
                        "function": "test_1",
                    },
                    {
                        "node_id": "test_module_1.py::test_2",
                        "node_type": "case",
                        "name": "test_2",
                        "doc": "This is a test docstring.",
                        "markers": [],
                        "parameters": {},
                        "path": directory.joinpath("test_module_1.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_module_1",
                        "suite": None,
                        "function": "test_2",
                    },
                ],
            },
            {
                "event": "collect_report",
                "session_id": "omitted",
                "node_id": "test_module_2.py",
                "timestamp": "omitted",
                "items": [
                    {
                        "node_id": "test_module_2.py::test_3",
                        "node_type": "case",
                        "name": "test_3",
                        "doc": "This is a test docstring.",
                        "markers": [],
                        "parameters": {},
                        "path": directory.joinpath("test_module_2.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_module_2",
                        "suite": None,
                        "function": "test_3",
                    },
                    {
                        "node_id": "test_module_2.py::test_4",
                        "node_type": "case",
                        "name": "test_4",
                        "doc": "This is a test docstring.",
                        "markers": [],
                        "parameters": {},
                        "path": directory.joinpath("test_module_2.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_module_2",
                        "suite": None,
                        "function": "test_4",
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
                        "node_id": "test_module_1.py",
                        "node_type": "module",
                        "name": "test_module_1.py",
                        "path": directory.joinpath("test_module_1.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "doc": "",
                        "markers": [],
                    },
                    {
                        "node_id": "test_module_2.py",
                        "node_type": "module",
                        "name": "test_module_2.py",
                        "path": directory.joinpath("test_module_2.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "doc": "",
                        "markers": [],
                    },
                ],
            },
            {
                "exit_status": 0,
                "event": "session_finish",
                "session_id": "omitted",
                "timestamp": "omitted",
            },
        ]
