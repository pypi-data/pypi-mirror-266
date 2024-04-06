from __future__ import annotations

from pathlib import Path

import pytest

from pytest_broadcaster import __version__

from ._utils import CommonTestSetup


@pytest.mark.basic
class TestBasic(CommonTestSetup):
    """Scenario: A single test case within a single test file."""

    def make_test_directory(self) -> Path:
        self.test_dir.mkdir("subdirectory_1")
        self.test_dir.mkdir("subdirectory_2")
        self.make_testfile(
            "subdirectory_1/test_module_1.py",
            """
            '''This is a module docstring.'''

            def test_1():
                '''This is a test docstring.'''
                pass
            """,
        )
        return self.make_testfile(
            "subdirectory_2/test_module_2.py",
            """
            '''This is a module docstring.'''

            def test_2():
                '''This is a test docstring.'''
                pass
            """,
        ).parent.parent

    def test_json(self):
        """Test JSON report for single test case within single test file."""

        directory = self.make_test_directory()
        result = self.test_dir.runpytest(
            "--collect-only", "--collect-report", self.json_file.as_posix()
        )
        assert result.ret == 0
        assert self.json_file.exists()
        assert self.read_json_file() == {
            "pytest_version": pytest.__version__,
            "plugin_version": __version__,
            "exit_status": 0,
            "errors": [],
            "warnings": [],
            "test_reports": [],
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
                    "node_id": "subdirectory_1/test_module_1.py",
                    "items": [
                        {
                            "node_id": "subdirectory_1/test_module_1.py::test_1",
                            "node_type": "case",
                            "name": "test_1",
                            "doc": "This is a test docstring.",
                            "markers": [],
                            "parameters": {},
                            "path": directory.joinpath(
                                "subdirectory_1/test_module_1.py"
                            )
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "subdirectory_1.test_module_1",
                            "suite": None,
                            "function": "test_1",
                        }
                    ],
                },
                {
                    "event": "collect_report",
                    "node_id": "subdirectory_1",
                    "items": [
                        {
                            "node_id": "subdirectory_1/test_module_1.py",
                            "name": "test_module_1.py",
                            "path": directory.joinpath(
                                "subdirectory_1/test_module_1.py"
                            )
                            .relative_to(directory.parent)
                            .as_posix(),
                            "doc": "This is a module docstring.",
                            "markers": [],
                            "node_type": "module",
                        }
                    ],
                },
                {
                    "event": "collect_report",
                    "node_id": "subdirectory_2/test_module_2.py",
                    "items": [
                        {
                            "node_id": "subdirectory_2/test_module_2.py::test_2",
                            "node_type": "case",
                            "name": "test_2",
                            "doc": "This is a test docstring.",
                            "markers": [],
                            "parameters": {},
                            "path": directory.joinpath(
                                "subdirectory_2/test_module_2.py"
                            )
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "subdirectory_2.test_module_2",
                            "suite": None,
                            "function": "test_2",
                        }
                    ],
                },
                {
                    "event": "collect_report",
                    "node_id": "subdirectory_2",
                    "items": [
                        {
                            "node_id": "subdirectory_2/test_module_2.py",
                            "name": "test_module_2.py",
                            "path": directory.joinpath(
                                "subdirectory_2/test_module_2.py"
                            )
                            .relative_to(directory.parent)
                            .as_posix(),
                            "doc": "This is a module docstring.",
                            "markers": [],
                            "node_type": "module",
                        }
                    ],
                },
                {
                    "node_id": ".",
                    "items": [
                        {
                            "node_id": "subdirectory_1",
                            "name": "subdirectory_1",
                            "path": directory.joinpath("subdirectory_1")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "node_type": "directory",
                        },
                        {
                            "node_id": "subdirectory_2",
                            "name": "subdirectory_2",
                            "path": directory.joinpath("subdirectory_2")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "node_type": "directory",
                        },
                    ],
                    "event": "collect_report",
                },
            ],
        }

    def test_jsonl_basic(self):
        """Test JSON Lines report for single test case within single test file."""

        directory = self.make_test_directory()
        result = self.test_dir.runpytest(
            "--collect-only", "--collect-log", self.json_lines_file.as_posix()
        )
        assert result.ret == 0
        assert self.json_lines_file.exists()
        assert self.read_json_lines_file() == [
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
                "node_id": "subdirectory_1/test_module_1.py",
                "items": [
                    {
                        "node_id": "subdirectory_1/test_module_1.py::test_1",
                        "node_type": "case",
                        "name": "test_1",
                        "doc": "This is a test docstring.",
                        "markers": [],
                        "parameters": {},
                        "path": directory.joinpath("subdirectory_1/test_module_1.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "subdirectory_1.test_module_1",
                        "suite": None,
                        "function": "test_1",
                    }
                ],
            },
            {
                "event": "collect_report",
                "node_id": "subdirectory_1",
                "items": [
                    {
                        "node_id": "subdirectory_1/test_module_1.py",
                        "name": "test_module_1.py",
                        "path": directory.joinpath("subdirectory_1/test_module_1.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "doc": "This is a module docstring.",
                        "markers": [],
                        "node_type": "module",
                    }
                ],
            },
            {
                "event": "collect_report",
                "node_id": "subdirectory_2/test_module_2.py",
                "items": [
                    {
                        "node_id": "subdirectory_2/test_module_2.py::test_2",
                        "node_type": "case",
                        "name": "test_2",
                        "doc": "This is a test docstring.",
                        "markers": [],
                        "parameters": {},
                        "path": directory.joinpath("subdirectory_2/test_module_2.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "subdirectory_2.test_module_2",
                        "suite": None,
                        "function": "test_2",
                    }
                ],
            },
            {
                "event": "collect_report",
                "node_id": "subdirectory_2",
                "items": [
                    {
                        "node_id": "subdirectory_2/test_module_2.py",
                        "name": "test_module_2.py",
                        "path": directory.joinpath("subdirectory_2/test_module_2.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "doc": "This is a module docstring.",
                        "markers": [],
                        "node_type": "module",
                    }
                ],
            },
            {
                "node_id": ".",
                "items": [
                    {
                        "node_id": "subdirectory_1",
                        "name": "subdirectory_1",
                        "path": directory.joinpath("subdirectory_1")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "node_type": "directory",
                    },
                    {
                        "node_id": "subdirectory_2",
                        "name": "subdirectory_2",
                        "path": directory.joinpath("subdirectory_2")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "node_type": "directory",
                    },
                ],
                "event": "collect_report",
            },
            {"exit_status": 0, "event": "session_finish"},
        ]
