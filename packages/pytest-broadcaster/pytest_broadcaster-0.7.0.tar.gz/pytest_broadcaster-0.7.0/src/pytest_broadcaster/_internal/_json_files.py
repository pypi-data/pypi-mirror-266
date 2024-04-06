from __future__ import annotations

import json
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, TextIO

from ..interfaces import Destination
from ..models.session_event import SessionEvent
from ..models.session_result import SessionResult


def _default_serializer(obj: object) -> object:
    if isinstance(obj, Enum):
        return obj.value
    return obj


def encode(obj: Any) -> str:
    return json.dumps(
        asdict(obj),
        default=_default_serializer,
    )


class JSONFile(Destination):
    def __init__(self, filepath: str) -> None:
        self.filepath = Path(filepath)

    def open(self) -> None:
        # Ensure the directory exists.
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def close(self) -> None:
        pass

    def write_result(self, result: SessionResult) -> None:
        json_data = json.dumps(
            asdict(result),
            default=_default_serializer,
        )
        self.filepath.write_text(json_data)

    def write_event(
        self,
        event: SessionEvent,
    ) -> None:
        # We don't write events to JSON file
        pass

    def summary(self) -> str | None:
        return f"generated report file: {self.filepath.as_posix()}"


class JSONLinesFile(Destination):
    def __init__(self, filepath: str) -> None:
        self.filepath = Path(filepath)
        self._file: TextIO | None = None

    def _open(self) -> None:
        if self._file is not None:
            raise RuntimeError("JSON Lines output file is already opened")
        # Ensure the directory exists.
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        # Open the text file in write mode.
        self._file = self.filepath.open("wt", buffering=1, encoding="UTF-8")

    def close(self) -> None:
        if self._file is None:
            return
        self._file.close()
        self._file = None

    def write_result(self, result: SessionResult) -> None:
        # We don't write results to JSON Lines
        pass

    def write_event(
        self,
        event: SessionEvent,
    ) -> None:
        if self._file is None:
            self._open()
            assert self._file is not None
        json_data = json.dumps(
            asdict(event),
            default=_default_serializer,
        )
        self._file.write(json_data + "\n")
        self._file.flush()

    def summary(self) -> str | None:
        return f"generated report log file: {self.filepath.as_posix()}"


if TYPE_CHECKING:
    # Make sure the class implements the interface.
    JSONFile("fake.json")
    # Make sure the class implements the interface.
    JSONLinesFile("fake.jsonl")
