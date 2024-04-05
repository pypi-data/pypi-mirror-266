from __future__ import annotations

from pathlib import Path

import pytest
from pytest_broadcaster import __version__

from ._utils import CommonTestSetup


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
        assert self.read_json_file() == {
            "pytest_version": pytest.__version__,
            "plugin_version": __version__,
            "exit_status": 0,
            "errors": [],
            "warnings": [],
            "test_reports": [],
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
                    "node_id": "test_module_1.py",
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
                    "event": "CollectReport",
                    "node_id": "test_module_2.py",
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
                    "event": "CollectReport",
                    "node_id": ".",
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
        assert self.read_json_lines_file() == [
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
                "node_id": "test_module_1.py",
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
                "event": "CollectReport",
                "node_id": "test_module_2.py",
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
                "event": "CollectReport",
                "node_id": ".",
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
            {"exit_status": 0, "event": "SessionFinish"},
        ]
