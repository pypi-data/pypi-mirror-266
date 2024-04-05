from __future__ import annotations

from pathlib import Path

import pytest
from fake_lib import filename
from pytest_broadcaster import __version__

from ._utils import CommonTestSetup


@pytest.mark.basic
class TestErrorsThirdParty(CommonTestSetup):
    """Errors test suite."""

    def make_basic_test(self) -> Path:
        """A helper function to make a test file which emits errors on collection."""

        return self.make_testfile(
            "test_errors.py",
            """
            '''This is a module docstring.'''
            import fake_lib.with_errors
            """,
        ).parent

    def test_json(self):
        """Test JSON report for test file with emit warnings on collection."""

        directory = self.make_basic_test()
        result = self.test_dir.runpytest(
            "--collect-only", "--collect-report", self.json_file.as_posix()
        )
        assert result.ret == 3
        assert self.json_file.exists()
        assert self.filter_traceback(self.read_json_file()) == {
            "pytest_version": pytest.__version__,
            "plugin_version": __version__,
            "exit_status": 3,
            "warnings": [],
            "errors": [
                {
                    "event": "ErrorMessage",
                    "when": "collect",
                    "location": {
                        "filename": filename("with_errors.py"),
                        "lineno": 1,
                    },
                    "traceback": {
                        "entries": [
                            {"path": "test_errors.py", "lineno": 2, "message": ""},
                            {
                                "path": filename("with_errors.py"),
                                "lineno": 1,
                                "message": "RuntimeError",
                            },
                        ]
                    },
                    "exception_type": "RuntimeError",
                    "exception_value": "BOOM",
                }
            ],
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
            ],
        }

    def test_jsonl(self):
        """Test JSON Lines report for test file which emits warnings on collection."""

        directory = self.make_basic_test()
        result = self.test_dir.runpytest(
            "--collect-only", "--collect-log", self.json_lines_file.as_posix()
        )
        assert result.ret == 3
        assert self.json_lines_file.exists()
        assert self.filter_traceback(self.read_json_lines_file()) == [
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
                "event": "ErrorMessage",
                "when": "collect",
                "location": {
                    "filename": filename("with_errors.py"),
                    "lineno": 1,
                },
                "traceback": {
                    "entries": [
                        {"path": "test_errors.py", "lineno": 2, "message": ""},
                        {
                            "path": filename("with_errors.py"),
                            "lineno": 1,
                            "message": "RuntimeError",
                        },
                    ]
                },
                "exception_type": "RuntimeError",
                "exception_value": "BOOM",
            },
            {"exit_status": 3, "event": "SessionFinish"},
        ]
