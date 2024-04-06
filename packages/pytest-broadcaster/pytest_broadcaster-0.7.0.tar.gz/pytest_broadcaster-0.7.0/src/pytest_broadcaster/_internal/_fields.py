from __future__ import annotations

import datetime
from warnings import WarningMessage

import pytest
from _pytest._code.code import ReprTraceback

from ._utils import (
    NodeID,
    TracebackLine,
    filter_traceback,
    format_mark,
    get_test_args,
    get_test_doc,
    get_test_markers,
    make_traceback_line,
    parse_node_id,
)


def make_node_id(
    item: pytest.Item | pytest.Directory | pytest.Module | pytest.Class,
) -> NodeID:
    mod, cls, func, params = parse_node_id(item.nodeid)
    name = "%s[%s]" % (func, params) if params else func
    filename = mod.split("/")[-1] if mod else None
    module = filename.replace(".py", "") if filename else None
    classes = cls.split("::") if cls else None
    return NodeID(
        filename=filename,
        module=module,
        classes=classes,
        func=func,
        params=params or None,
        name=name,
        value=item.nodeid,
    )


def field_doc(item: pytest.Item | pytest.Module | pytest.Class) -> str:
    return get_test_doc(item).strip()


def field_markers(
    item: pytest.Item | pytest.Directory | pytest.Module | pytest.Class,
) -> list[str]:
    return list(
        set(
            [
                format_mark(mark)
                for mark in sorted(get_test_markers(item), key=lambda mark: mark.name)
            ]
        )
    )


def field_parameters(item: pytest.Item) -> dict[str, str]:
    return {k: type(v).__name__ for k, v in sorted(get_test_args(item).items())}


def make_warning_message(warning: WarningMessage) -> str:
    if isinstance(warning.message, str):
        return warning.message
    return str(warning.message)


def make_timestamp(epoch: float) -> str:
    return datetime.datetime.fromtimestamp(epoch).isoformat()


def make_traceback(report: pytest.TestReport) -> list[TracebackLine]:
    return make_traceback_from_reprtraceback(report.longrepr.reprtraceback)  # type: ignore


def make_traceback_from_reprtraceback(
    reprtraceback: ReprTraceback,
) -> list[TracebackLine]:
    return [
        make_traceback_line(line.reprfileloc)  # type: ignore
        for line in reprtraceback.reprentries
        if filter_traceback(line.reprfileloc.path)  # type: ignore
    ]
