from __future__ import annotations

from pathlib import Path

import pytest
from pytest_broadcaster import __version__

from ._utils import CommonTestSetup


@pytest.mark.basic
@pytest.mark.parametrization
class TestBasicParametrization(CommonTestSetup):
    """Scenario: A single test case with parametrize within a single test file."""

    def make_test_directory(self) -> Path:
        return self.make_testfile(
            "test_basic_parametrization.py",
            """
            import pytest

            @pytest.mark.parametrize("arg", [1, 2, 3])
            def test_ok(arg: int):
                pass
        """,
        ).parent

    def test_json(self):
        """Test JSON report for a test file with a single test case with parametrize."""

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
                    "node_id": "test_basic_parametrization.py",
                    "items": [
                        {
                            "node_id": "test_basic_parametrization.py::test_ok[1]",
                            "node_type": "case",
                            "name": "test_ok[1]",
                            "doc": "",
                            "markers": ["parametrize"],
                            "parameters": {"arg": "int"},
                            "path": directory.joinpath("test_basic_parametrization.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_basic_parametrization",
                            "suite": None,
                            "function": "test_ok",
                        },
                        {
                            "node_id": "test_basic_parametrization.py::test_ok[2]",
                            "node_type": "case",
                            "name": "test_ok[2]",
                            "doc": "",
                            "markers": ["parametrize"],
                            "parameters": {"arg": "int"},
                            "path": directory.joinpath("test_basic_parametrization.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_basic_parametrization",
                            "suite": None,
                            "function": "test_ok",
                        },
                        {
                            "node_id": "test_basic_parametrization.py::test_ok[3]",
                            "node_type": "case",
                            "name": "test_ok[3]",
                            "doc": "",
                            "markers": ["parametrize"],
                            "parameters": {"arg": "int"},
                            "path": directory.joinpath("test_basic_parametrization.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_basic_parametrization",
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
                            "node_id": "test_basic_parametrization.py",
                            "name": "test_basic_parametrization.py",
                            "path": directory.joinpath("test_basic_parametrization.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "doc": "",
                            "markers": [],
                            "node_type": "module",
                        }
                    ],
                },
            ],
        }

    def test_jsonl(self):
        """Test JSON Lines report for a test file with a single test case with parametrize."""

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
                "items": [
                    {
                        "node_id": "test_basic_parametrization.py::test_ok[1]",
                        "node_type": "case",
                        "name": "test_ok[1]",
                        "doc": "",
                        "markers": ["parametrize"],
                        "parameters": {"arg": "int"},
                        "path": directory.joinpath("test_basic_parametrization.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_basic_parametrization",
                        "suite": None,
                        "function": "test_ok",
                    },
                    {
                        "node_id": "test_basic_parametrization.py::test_ok[2]",
                        "node_type": "case",
                        "name": "test_ok[2]",
                        "doc": "",
                        "markers": ["parametrize"],
                        "parameters": {"arg": "int"},
                        "path": directory.joinpath("test_basic_parametrization.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_basic_parametrization",
                        "suite": None,
                        "function": "test_ok",
                    },
                    {
                        "node_id": "test_basic_parametrization.py::test_ok[3]",
                        "node_type": "case",
                        "name": "test_ok[3]",
                        "doc": "",
                        "markers": ["parametrize"],
                        "parameters": {"arg": "int"},
                        "path": directory.joinpath("test_basic_parametrization.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_basic_parametrization",
                        "suite": None,
                        "function": "test_ok",
                    },
                ],
                "event": "CollectReport",
                "node_id": "test_basic_parametrization.py",
            },
            {
                "event": "CollectReport",
                "node_id": ".",
                "items": [
                    {
                        "node_id": "test_basic_parametrization.py",
                        "name": "test_basic_parametrization.py",
                        "path": directory.joinpath("test_basic_parametrization.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "doc": "",
                        "markers": [],
                        "node_type": "module",
                    }
                ],
            },
            {"exit_status": 0, "event": "SessionFinish"},
        ]
