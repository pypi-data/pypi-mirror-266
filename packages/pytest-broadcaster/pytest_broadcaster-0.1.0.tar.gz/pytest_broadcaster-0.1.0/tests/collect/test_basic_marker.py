from __future__ import annotations

from pathlib import Path

import pytest
from pytest_broadcaster import __version__

from ._utils import CommonTestSetup


@pytest.mark.basic
@pytest.mark.markers
class TestBasicMarker(CommonTestSetup):
    """Scenario: A single test case with a marker within a single test file."""

    def make_test_directory(self) -> Path:
        return self.make_testfile(
            "test_basic_marker.py",
            """
            import pytest

            @pytest.mark.skip
            def test_ok():
                pass
        """,
        ).parent

    def test_json_basic_marker(self):
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
                    "node_id": "test_basic_marker.py",
                    "items": [
                        {
                            "node_id": "test_basic_marker.py::test_ok",
                            "node_type": "case",
                            "name": "test_ok",
                            "doc": "",
                            "markers": ["skip"],
                            "parameters": {},
                            "path": directory.joinpath("test_basic_marker.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_basic_marker",
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
                            "node_id": "test_basic_marker.py",
                            "name": "test_basic_marker.py",
                            "path": directory.joinpath("test_basic_marker.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "markers": [],
                            "doc": "",
                            "node_type": "module",
                        }
                    ],
                },
            ],
        }

    def test_jsonl_basic_marker(self):
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
                "node_id": "test_basic_marker.py",
                "items": [
                    {
                        "node_id": "test_basic_marker.py::test_ok",
                        "node_type": "case",
                        "name": "test_ok",
                        "doc": "",
                        "markers": ["skip"],
                        "parameters": {},
                        "path": directory.joinpath("test_basic_marker.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_basic_marker",
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
                        "node_id": "test_basic_marker.py",
                        "node_type": "module",
                        "name": "test_basic_marker.py",
                        "path": directory.joinpath("test_basic_marker.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "doc": "",
                        "markers": [],
                    }
                ],
            },
            {"exit_status": 0, "event": "SessionFinish"},
        ]
