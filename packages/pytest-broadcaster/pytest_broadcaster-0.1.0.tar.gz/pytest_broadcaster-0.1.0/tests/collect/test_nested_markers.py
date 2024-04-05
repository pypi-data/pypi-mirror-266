from __future__ import annotations

from pathlib import Path

import pytest
from pytest_broadcaster import __version__

from ._utils import CommonTestSetup


@pytest.mark.markers
class TestNestedMarker(CommonTestSetup):
    """Scenario: A test suite with a marker and a single test with same marker."""

    def make_test_directory(self) -> Path:
        return self.make_testfile(
            "test_markers.py",
            """
            import pytest

            @pytest.mark.skip
            class TestMarked:
                @pytest.mark.skip
                def test_marked():
                    pass
        """,
        ).parent

    def test_json(self):
        """Test JSON report for a test file with a single test case with a marker."""

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
                    "node_id": "test_markers.py::TestMarked",
                    "items": [
                        {
                            "node_id": "test_markers.py::TestMarked::test_marked",
                            "node_type": "case",
                            "name": "test_marked",
                            "doc": "",
                            "markers": ["skip"],
                            "parameters": {},
                            "path": directory.joinpath("test_markers.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_markers",
                            "suite": "TestMarked",
                            "function": "test_marked",
                        },
                    ],
                },
                {
                    "event": "CollectReport",
                    "node_id": "test_markers.py",
                    "items": [
                        {
                            "node_id": "test_markers.py::TestMarked",
                            "node_type": "suite",
                            "name": "TestMarked",
                            "path": directory.joinpath("test_markers.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_markers",
                            "doc": "",
                            "markers": ["skip"],
                        }
                    ],
                },
                {
                    "event": "CollectReport",
                    "node_id": ".",
                    "items": [
                        {
                            "node_id": "test_markers.py",
                            "node_type": "module",
                            "name": "test_markers.py",
                            "path": directory.joinpath("test_markers.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "doc": "",
                            "markers": [],
                        }
                    ],
                },
            ],
        }

    def test_jsonl(self):
        """Test JSON Lines report for a test file with a single test case with a marker."""

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
                "node_id": "test_markers.py::TestMarked",
                "items": [
                    {
                        "node_id": "test_markers.py::TestMarked::test_marked",
                        "node_type": "case",
                        "name": "test_marked",
                        "doc": "",
                        "markers": ["skip"],
                        "parameters": {},
                        "path": directory.joinpath("test_markers.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_markers",
                        "suite": "TestMarked",
                        "function": "test_marked",
                    },
                ],
            },
            {
                "event": "CollectReport",
                "node_id": "test_markers.py",
                "items": [
                    {
                        "node_id": "test_markers.py::TestMarked",
                        "node_type": "suite",
                        "name": "TestMarked",
                        "path": directory.joinpath("test_markers.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_markers",
                        "doc": "",
                        "markers": ["skip"],
                    }
                ],
            },
            {
                "event": "CollectReport",
                "node_id": ".",
                "items": [
                    {
                        "node_id": "test_markers.py",
                        "node_type": "module",
                        "name": "test_markers.py",
                        "path": directory.joinpath("test_markers.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "doc": "",
                        "markers": [],
                    }
                ],
            },
            {"exit_status": 0, "event": "SessionFinish"},
        ]
