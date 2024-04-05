from __future__ import annotations

from pathlib import Path

import pytest
from pytest_broadcaster import __version__

from ._utils import CommonTestSetup


@pytest.mark.suites
@pytest.mark.basic
class TestBasicSuite(CommonTestSetup):
    """Scenario: several tests cases within a single test suite within a single test file."""

    def make_test_directory(self) -> Path:
        return self.make_testfile(
            "test_basic_suite.py",
            """
            '''This is a module docstring.'''
            class TestOk:
                '''This is a suite docstring.'''
                def test_1():
                    '''This is a first docstring.'''
                    pass
                def test_2():
                    '''This is a second docstring.'''
                    pass
            """,
        ).parent

    def test_json(self):
        """Test JSON report for single test suite within a single test file."""

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
                    "node_id": "test_basic_suite.py::TestOk",
                    "items": [
                        {
                            "node_id": "test_basic_suite.py::TestOk::test_1",
                            "node_type": "case",
                            "name": "test_1",
                            "doc": "This is a first docstring.",
                            "markers": [],
                            "parameters": {},
                            "path": directory.joinpath("test_basic_suite.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_basic_suite",
                            "suite": "TestOk",
                            "function": "test_1",
                        },
                        {
                            "node_id": "test_basic_suite.py::TestOk::test_2",
                            "node_type": "case",
                            "name": "test_2",
                            "doc": "This is a second docstring.",
                            "markers": [],
                            "parameters": {},
                            "path": directory.joinpath("test_basic_suite.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_basic_suite",
                            "suite": "TestOk",
                            "function": "test_2",
                        },
                    ],
                },
                {
                    "event": "CollectReport",
                    "node_id": "test_basic_suite.py",
                    "items": [
                        {
                            "node_id": "test_basic_suite.py::TestOk",
                            "node_type": "suite",
                            "name": "TestOk",
                            "path": directory.joinpath("test_basic_suite.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_basic_suite",
                            "doc": "This is a suite docstring.",
                            "markers": [],
                        }
                    ],
                },
                {
                    "event": "CollectReport",
                    "node_id": ".",
                    "items": [
                        {
                            "node_id": "test_basic_suite.py",
                            "node_type": "module",
                            "name": "test_basic_suite.py",
                            "path": directory.joinpath("test_basic_suite.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "doc": "This is a module docstring.",
                            "markers": [],
                        }
                    ],
                },
            ],
        }

    def test_jsonl(self):
        """Test JSON Lines report for single test suite within a single test file."""

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
                "node_id": "test_basic_suite.py::TestOk",
                "items": [
                    {
                        "node_id": "test_basic_suite.py::TestOk::test_1",
                        "node_type": "case",
                        "name": "test_1",
                        "doc": "This is a first docstring.",
                        "markers": [],
                        "parameters": {},
                        "path": directory.joinpath("test_basic_suite.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_basic_suite",
                        "suite": "TestOk",
                        "function": "test_1",
                    },
                    {
                        "node_id": "test_basic_suite.py::TestOk::test_2",
                        "node_type": "case",
                        "name": "test_2",
                        "doc": "This is a second docstring.",
                        "markers": [],
                        "parameters": {},
                        "path": directory.joinpath("test_basic_suite.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_basic_suite",
                        "suite": "TestOk",
                        "function": "test_2",
                    },
                ],
            },
            {
                "event": "CollectReport",
                "node_id": "test_basic_suite.py",
                "items": [
                    {
                        "node_id": "test_basic_suite.py::TestOk",
                        "node_type": "suite",
                        "name": "TestOk",
                        "path": directory.joinpath("test_basic_suite.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "doc": "This is a suite docstring.",
                        "module": "test_basic_suite",
                        "markers": [],
                    }
                ],
            },
            {
                "event": "CollectReport",
                "node_id": ".",
                "items": [
                    {
                        "node_id": "test_basic_suite.py",
                        "node_type": "module",
                        "name": "test_basic_suite.py",
                        "path": directory.joinpath("test_basic_suite.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "doc": "This is a module docstring.",
                        "markers": [],
                    }
                ],
            },
            {"exit_status": 0, "event": "SessionFinish"},
        ]
