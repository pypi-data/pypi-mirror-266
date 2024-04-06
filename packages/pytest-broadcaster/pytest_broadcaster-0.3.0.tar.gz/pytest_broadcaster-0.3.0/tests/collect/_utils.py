from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest


class CommonTestSetup:
    @pytest.fixture(autouse=True)
    def setup(
        self, pytester: pytest.Pytester, tmp_path: Path, pytestconfig: pytest.Config
    ):
        self.tmp_path = tmp_path
        self.test_dir = pytester
        self.pytestconfig = pytestconfig
        self.json_file = self.tmp_path.joinpath("collect.json")
        self.json_lines_file = self.tmp_path.joinpath("collect.jsonl")

    def read_json_file(self) -> dict[str, Any]:
        return json.loads(self.json_file.read_text())

    def read_json_lines_file(self) -> list[dict[str, Any]]:
        return [
            json.loads(line.strip())
            for line in self.json_lines_file.read_text().splitlines()
            if line.strip()
        ]

    def make_testfile(self, filename: str, content: str) -> Path:
        if filename.endswith(".py"):
            filename = filename[:-3]
        else:
            raise ValueError("Filename must end with '.py'")
        kwargs = {filename: content}
        return self.test_dir.makepyfile(**kwargs)

    def filter_traceback(
        self, data: dict[str, Any] | list[Any]
    ) -> dict[str, Any] | list[Any]:
        return self._filter_traceback(deepcopy(data))

    def _filter_traceback(
        self,
        data: Any,
    ) -> Any:
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "traceback":
                    data[key] = {
                        **data[key],
                        "entries": [
                            line
                            for line in value["entries"]
                            if (
                                "importlib" not in line["path"]
                                and "pytest_asyncio" not in line["path"]
                            )
                        ],
                    }
                elif isinstance(value, dict):
                    data[key] = self._filter_traceback(value)
                elif isinstance(value, list):
                    data[key] = self._filter_traceback(value)
        elif isinstance(data, list):
            data = [self._filter_traceback(item) for item in data]
        else:
            return data
        return data
