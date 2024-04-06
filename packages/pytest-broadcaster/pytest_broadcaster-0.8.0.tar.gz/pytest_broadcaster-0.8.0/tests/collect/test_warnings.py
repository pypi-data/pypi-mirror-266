from __future__ import annotations

import sys
from pathlib import Path

import pytest

from _testing.setup import CommonTestSetup
from pytest_broadcaster import __version__


@pytest.mark.basic
class TestWarnings(CommonTestSetup):
    """Warnings test suite."""

    def make_basic_test(self) -> Path:
        """A helper function to make a test file which emits warnings on collection."""

        return self.make_testfile(
            "test_warnings.py",
            """
            import warnings

            warnings.warn("HEY, YOU'BE BEEN WARNED")
            warnings.warn("HEY, YOU'BE BEEN WARNED TWICE !")

            def test_warn():
                '''This is a test docstring.'''
                pass
            """,
        ).parent

    def test_json(self):
        """Test JSON report for test file with emit warnings on collection."""

        directory = self.make_basic_test()
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
            "warnings": [
                {
                    "when": "collect",
                    "node_id": "",
                    "location": {
                        "filename": directory.joinpath("test_warnings.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "lineno": 3,
                    },
                    "message": "HEY, YOU'BE BEEN WARNED",
                    "event": "warning_message",
                    "category": "UserWarning",
                },
                {
                    "when": "collect",
                    "node_id": "",
                    "message": "HEY, YOU'BE BEEN WARNED TWICE !",
                    "event": "warning_message",
                    "location": {
                        "filename": directory.joinpath("test_warnings.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "lineno": 4,
                    },
                    "category": "UserWarning",
                },
            ],
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
                    "node_id": "test_warnings.py",
                    "timestamp": "omitted",
                    "items": [
                        {
                            "node_id": "test_warnings.py::test_warn",
                            "node_type": "case",
                            "name": "test_warn",
                            "doc": "This is a test docstring.",
                            "markers": [],
                            "parameters": {},
                            "path": directory.joinpath("test_warnings.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "module": "test_warnings",
                            "suite": None,
                            "function": "test_warn",
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
                            "node_id": "test_warnings.py",
                            "node_type": "module",
                            "name": "test_warnings.py",
                            "path": directory.joinpath("test_warnings.py")
                            .relative_to(directory.parent)
                            .as_posix(),
                            "doc": "",
                            "markers": [],
                        }
                    ],
                },
            ],
            "test_reports": [],
        }

    def test_jsonl(self):
        """Test JSON Lines report for test file which emits warnings on collection."""

        directory = self.make_basic_test()
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
                "node_id": "test_warnings.py",
                "timestamp": "omitted",
                "items": [
                    {
                        "node_id": "test_warnings.py::test_warn",
                        "node_type": "case",
                        "name": "test_warn",
                        "doc": "This is a test docstring.",
                        "markers": [],
                        "parameters": {},
                        "path": directory.joinpath("test_warnings.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "module": "test_warnings",
                        "suite": None,
                        "function": "test_warn",
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
                        "node_id": "test_warnings.py",
                        "node_type": "module",
                        "name": "test_warnings.py",
                        "path": directory.joinpath("test_warnings.py")
                        .relative_to(directory.parent)
                        .as_posix(),
                        "doc": "",
                        "markers": [],
                    }
                ],
            },
            {
                "when": "collect",
                "node_id": "",
                "location": {
                    "filename": directory.joinpath("test_warnings.py")
                    .relative_to(directory.parent)
                    .as_posix(),
                    "lineno": 3,
                },
                "message": "HEY, YOU'BE BEEN WARNED",
                "event": "warning_message",
                "category": "UserWarning",
            },
            {
                "when": "collect",
                "node_id": "",
                "location": {
                    "filename": directory.joinpath("test_warnings.py")
                    .relative_to(directory.parent)
                    .as_posix(),
                    "lineno": 4,
                },
                "message": "HEY, YOU'BE BEEN WARNED TWICE !",
                "event": "warning_message",
                "category": "UserWarning",
            },
            {
                "exit_status": 0,
                "event": "session_finish",
                "session_id": "omitted",
                "timestamp": "omitted",
            },
        ]
