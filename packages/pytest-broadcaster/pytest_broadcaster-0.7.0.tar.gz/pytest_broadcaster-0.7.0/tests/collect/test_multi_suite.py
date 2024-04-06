from __future__ import annotations

from pathlib import Path

import pytest

from pytest_broadcaster import __version__

from ._utils import CommonTestSetup


@pytest.mark.suites
@pytest.mark.filetree
class TestMultiSuite(CommonTestSetup):
    """Scenario: Several test suites within several test files."""

    def make_test_directory(self) -> Path:
        self.make_testfile(
            "test_module_1.py",
            """
            class TestSuite1:
                '''This is a suite docstring.'''
                def test_1():
                    '''This is a first docstring.'''
                    pass
                def test_2():
                    '''This is a second docstring.'''
                    pass
            class TestSuite2:
                '''This is a suite docstring.'''
                def test_3():
                    '''This is a third docstring.'''
                    pass
                def test_4():
                    '''This is a fourth docstring.'''
                    pass
            """,
        )
        return self.make_testfile(
            "test_module_2.py",
            """
            class TestSuite3:
                '''This is a suite docstring.'''
                def test_5():
                    '''This is a fifth docstring.'''
                    pass
                def test_6():
                    '''This is a sixth docstring.'''
                    pass
            class TestSuite4:
                '''This is a suite docstring.'''
                def test_7():
                    '''This is a seventh docstring.'''
                    pass
                def test_8():
                    '''This is a eighth docstring.'''
                    pass
            """,
        ).parent

    def test_json(self):
        """Test JSON report for several test suites within several test files."""

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
                    "node_id": "test_module_1.py::TestSuite1",
                    "items": [
                        {
                            "node_id": "test_module_1.py::TestSuite1::test_1",
                            "node_type": "case",
                            "name": "test_1",
                            "doc": "This is a first docstring.",
                            "markers": [],
                            "parameters": {},
                            "path": directory.joinpath("test_module_1.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_module_1",
                            "suite": "TestSuite1",
                            "function": "test_1",
                        },
                        {
                            "node_id": "test_module_1.py::TestSuite1::test_2",
                            "node_type": "case",
                            "name": "test_2",
                            "doc": "This is a second docstring.",
                            "markers": [],
                            "parameters": {},
                            "path": directory.joinpath("test_module_1.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_module_1",
                            "suite": "TestSuite1",
                            "function": "test_2",
                        },
                    ],
                },
                {
                    "event": "collect_report",
                    "node_id": "test_module_1.py::TestSuite2",
                    "items": [
                        {
                            "node_id": "test_module_1.py::TestSuite2::test_3",
                            "node_type": "case",
                            "name": "test_3",
                            "doc": "This is a third docstring.",
                            "markers": [],
                            "parameters": {},
                            "path": directory.joinpath("test_module_1.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_module_1",
                            "suite": "TestSuite2",
                            "function": "test_3",
                        },
                        {
                            "node_id": "test_module_1.py::TestSuite2::test_4",
                            "node_type": "case",
                            "name": "test_4",
                            "doc": "This is a fourth docstring.",
                            "markers": [],
                            "parameters": {},
                            "path": directory.joinpath("test_module_1.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_module_1",
                            "suite": "TestSuite2",
                            "function": "test_4",
                        },
                    ],
                },
                {
                    "event": "collect_report",
                    "node_id": "test_module_1.py",
                    "items": [
                        {
                            "node_id": "test_module_1.py::TestSuite1",
                            "node_type": "suite",
                            "name": "TestSuite1",
                            "path": directory.joinpath("test_module_1.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_module_1",
                            "markers": [],
                            "doc": "This is a suite docstring.",
                        },
                        {
                            "node_id": "test_module_1.py::TestSuite2",
                            "node_type": "suite",
                            "name": "TestSuite2",
                            "path": directory.joinpath("test_module_1.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_module_1",
                            "doc": "This is a suite docstring.",
                            "markers": [],
                        },
                    ],
                },
                {
                    "event": "collect_report",
                    "node_id": "test_module_2.py::TestSuite3",
                    "items": [
                        {
                            "node_id": "test_module_2.py::TestSuite3::test_5",
                            "node_type": "case",
                            "name": "test_5",
                            "doc": "This is a fifth docstring.",
                            "markers": [],
                            "parameters": {},
                            "path": directory.joinpath("test_module_2.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_module_2",
                            "suite": "TestSuite3",
                            "function": "test_5",
                        },
                        {
                            "node_id": "test_module_2.py::TestSuite3::test_6",
                            "node_type": "case",
                            "name": "test_6",
                            "doc": "This is a sixth docstring.",
                            "markers": [],
                            "parameters": {},
                            "path": directory.joinpath("test_module_2.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_module_2",
                            "suite": "TestSuite3",
                            "function": "test_6",
                        },
                    ],
                },
                {
                    "event": "collect_report",
                    "node_id": "test_module_2.py::TestSuite4",
                    "items": [
                        {
                            "node_id": "test_module_2.py::TestSuite4::test_7",
                            "node_type": "case",
                            "name": "test_7",
                            "doc": "This is a seventh docstring.",
                            "markers": [],
                            "parameters": {},
                            "path": directory.joinpath("test_module_2.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_module_2",
                            "suite": "TestSuite4",
                            "function": "test_7",
                        },
                        {
                            "node_id": "test_module_2.py::TestSuite4::test_8",
                            "node_type": "case",
                            "name": "test_8",
                            "doc": "This is a eighth docstring.",
                            "markers": [],
                            "parameters": {},
                            "path": directory.joinpath("test_module_2.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_module_2",
                            "suite": "TestSuite4",
                            "function": "test_8",
                        },
                    ],
                },
                {
                    "event": "collect_report",
                    "node_id": "test_module_2.py",
                    "items": [
                        {
                            "node_id": "test_module_2.py::TestSuite3",
                            "node_type": "suite",
                            "name": "TestSuite3",
                            "path": directory.joinpath("test_module_2.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_module_2",
                            "doc": "This is a suite docstring.",
                            "markers": [],
                        },
                        {
                            "node_id": "test_module_2.py::TestSuite4",
                            "node_type": "suite",
                            "name": "TestSuite4",
                            "path": directory.joinpath("test_module_2.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_module_2",
                            "doc": "This is a suite docstring.",
                            "markers": [],
                        },
                    ],
                },
                {
                    "event": "collect_report",
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
        """Test JSON Lines report for several test suites within several test files."""

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
                "node_id": "test_module_1.py::TestSuite1",
                "items": [
                    {
                        "node_id": "test_module_1.py::TestSuite1::test_1",
                        "node_type": "case",
                        "name": "test_1",
                        "doc": "This is a first docstring.",
                        "markers": [],
                        "parameters": {},
                        "path": directory.joinpath("test_module_1.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_module_1",
                        "suite": "TestSuite1",
                        "function": "test_1",
                    },
                    {
                        "node_id": "test_module_1.py::TestSuite1::test_2",
                        "node_type": "case",
                        "name": "test_2",
                        "doc": "This is a second docstring.",
                        "markers": [],
                        "parameters": {},
                        "path": directory.joinpath("test_module_1.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_module_1",
                        "suite": "TestSuite1",
                        "function": "test_2",
                    },
                ],
            },
            {
                "event": "collect_report",
                "node_id": "test_module_1.py::TestSuite2",
                "items": [
                    {
                        "node_id": "test_module_1.py::TestSuite2::test_3",
                        "node_type": "case",
                        "name": "test_3",
                        "doc": "This is a third docstring.",
                        "markers": [],
                        "parameters": {},
                        "path": directory.joinpath("test_module_1.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_module_1",
                        "suite": "TestSuite2",
                        "function": "test_3",
                    },
                    {
                        "node_id": "test_module_1.py::TestSuite2::test_4",
                        "node_type": "case",
                        "name": "test_4",
                        "doc": "This is a fourth docstring.",
                        "markers": [],
                        "parameters": {},
                        "path": directory.joinpath("test_module_1.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_module_1",
                        "suite": "TestSuite2",
                        "function": "test_4",
                    },
                ],
            },
            {
                "event": "collect_report",
                "node_id": "test_module_1.py",
                "items": [
                    {
                        "node_id": "test_module_1.py::TestSuite1",
                        "node_type": "suite",
                        "name": "TestSuite1",
                        "path": directory.joinpath("test_module_1.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_module_1",
                        "doc": "This is a suite docstring.",
                        "markers": [],
                    },
                    {
                        "node_id": "test_module_1.py::TestSuite2",
                        "node_type": "suite",
                        "name": "TestSuite2",
                        "path": directory.joinpath("test_module_1.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_module_1",
                        "doc": "This is a suite docstring.",
                        "markers": [],
                    },
                ],
            },
            {
                "event": "collect_report",
                "node_id": "test_module_2.py::TestSuite3",
                "items": [
                    {
                        "node_id": "test_module_2.py::TestSuite3::test_5",
                        "node_type": "case",
                        "name": "test_5",
                        "doc": "This is a fifth docstring.",
                        "markers": [],
                        "parameters": {},
                        "path": directory.joinpath("test_module_2.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_module_2",
                        "suite": "TestSuite3",
                        "function": "test_5",
                    },
                    {
                        "node_id": "test_module_2.py::TestSuite3::test_6",
                        "node_type": "case",
                        "name": "test_6",
                        "doc": "This is a sixth docstring.",
                        "markers": [],
                        "parameters": {},
                        "path": directory.joinpath("test_module_2.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_module_2",
                        "suite": "TestSuite3",
                        "function": "test_6",
                    },
                ],
            },
            {
                "event": "collect_report",
                "node_id": "test_module_2.py::TestSuite4",
                "items": [
                    {
                        "node_id": "test_module_2.py::TestSuite4::test_7",
                        "node_type": "case",
                        "name": "test_7",
                        "doc": "This is a seventh docstring.",
                        "markers": [],
                        "parameters": {},
                        "path": directory.joinpath("test_module_2.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_module_2",
                        "suite": "TestSuite4",
                        "function": "test_7",
                    },
                    {
                        "node_id": "test_module_2.py::TestSuite4::test_8",
                        "node_type": "case",
                        "name": "test_8",
                        "doc": "This is a eighth docstring.",
                        "markers": [],
                        "parameters": {},
                        "path": directory.joinpath("test_module_2.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_module_2",
                        "suite": "TestSuite4",
                        "function": "test_8",
                    },
                ],
            },
            {
                "event": "collect_report",
                "node_id": "test_module_2.py",
                "items": [
                    {
                        "node_id": "test_module_2.py::TestSuite3",
                        "node_type": "suite",
                        "name": "TestSuite3",
                        "path": directory.joinpath("test_module_2.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_module_2",
                        "doc": "This is a suite docstring.",
                        "markers": [],
                    },
                    {
                        "node_id": "test_module_2.py::TestSuite4",
                        "node_type": "suite",
                        "name": "TestSuite4",
                        "path": directory.joinpath("test_module_2.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_module_2",
                        "doc": "This is a suite docstring.",
                        "markers": [],
                    },
                ],
            },
            {
                "event": "collect_report",
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
            {"exit_status": 0, "event": "session_finish"},
        ]
