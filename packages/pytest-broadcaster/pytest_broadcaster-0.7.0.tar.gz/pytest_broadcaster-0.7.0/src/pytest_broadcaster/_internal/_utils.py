from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
from _pytest._code.code import (
    _PLUGGY_DIR,  # pyright: ignore[reportPrivateUsage]
    _PYTEST_DIR,  # pyright: ignore[reportPrivateUsage]
    ReprFileLocation,
)
from _pytest.outcomes import Skipped

__NODE_ID__ = re.compile(
    r"(?P<module>.+)\.py(?:::(?P<class>[^:]+)(?:::.+)?)?::(?P<function>[^\[]+)(?:\[(?P<params>.*)\])?"
)


@dataclass
class NodeID:
    filename: str | None
    module: str | None
    classes: list[str] | None
    func: str
    params: str | None
    name: str
    value: str = field(repr=False)

    def __str__(self) -> str:
        return self.value

    def suite(self) -> str | None:
        if self.classes:
            return "::".join(self.classes)
        return None


@dataclass
class TracebackLine:
    path: str
    lineno: int
    message: str


def parse_node_id(node_id: str) -> tuple[str, str, str, str]:
    match = re.search(__NODE_ID__, node_id)
    if match:
        return (
            match.group("module").replace("/", "."),
            match.group("class") or "",
            match.group("function"),
            match.group("params") or "",
        )
    raise Exception('Failed parsing pytest node id: "%s"' % node_id)


def get_test_doc(item: pytest.Item | pytest.Module | pytest.Class) -> str:
    try:
        return item.obj.__doc__ or ""  # type: ignore
    except (AttributeError, Skipped):
        return ""


def get_test_args(item: pytest.Item) -> dict[str, Any]:
    try:
        return item.callspec.params  # type: ignore
    except AttributeError:
        return {}


def get_test_markers(
    item: pytest.Item | pytest.Directory | pytest.Module | pytest.Class,
) -> list[pytest.Mark]:
    return list(item.iter_markers())


def format_mark(mark: pytest.Mark) -> str:
    return mark.name


def filter_traceback(raw_filename: str) -> bool:
    """Return True if a TracebackEntry instance should be included in tracebacks.

    We hide traceback entries of:

    * dynamically generated code (no code to show up for it);
    * internal traceback from pytest or its internal libraries, py and pluggy.
    """
    is_generated = "<" in raw_filename and ">" in raw_filename
    if is_generated:
        return False

    p = Path(raw_filename)

    parents = p.parents
    if _PLUGGY_DIR in parents:
        return False
    if _PYTEST_DIR in parents:
        return False

    return True


def make_traceback_line(loc: ReprFileLocation) -> TracebackLine:
    """Return JSON-serializable file location representation.

    See `_pytest._code.code.ReprFileLocation`.
    """
    return TracebackLine(
        path=loc.path,
        lineno=loc.lineno,
        message=loc.message,
    )
