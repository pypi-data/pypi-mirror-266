from __future__ import annotations

import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import pytest

from ..__about__ import __version__
from ..interfaces import Reporter
from ..models.collect_report import CollectReport
from ..models.error_message import ErrorMessage
from ..models.location import Location
from ..models.outcome import Outcome
from ..models.session_finish import SessionFinish
from ..models.session_result import SessionResult
from ..models.session_start import SessionStart
from ..models.test_case import TestCase
from ..models.test_case_call import TestCaseCall
from ..models.test_case_error import TestCaseError
from ..models.test_case_finished import TestCaseFinished
from ..models.test_case_report import TestCaseReport
from ..models.test_case_setup import TestCaseSetup
from ..models.test_case_teardown import TestCaseTeardown
from ..models.test_directory import TestDirectory
from ..models.test_module import TestModule
from ..models.test_suite import TestSuite
from ..models.traceback import Entry, Traceback
from ..models.warning_message import WarningMessage
from . import _fields as api


class DefaultReporter(Reporter):
    def __init__(self) -> None:
        self._roots: dict[str, str] = {}
        self._pending_report: TestCaseReport | None = None
        self._result = SessionResult(
            pytest_version=pytest.__version__,
            plugin_version=__version__,
            exit_status=0,
            warnings=[],
            errors=[],
            collect_reports=[],
            test_reports=[],
        )
        self._done = False

    def _get_path(self, path: str, is_error_or_warning: bool = False) -> str:
        for root in self._roots:
            if path.startswith(root):
                return self._roots[root] + "/" + path[len(root) + 1 :]
        pathobj = Path(path)
        if pathobj.is_dir():
            self._roots[path] = pathobj.name
            return pathobj.name
        if pathobj.is_file():
            if not is_error_or_warning:
                self._roots[path] = pathobj.parent.name
                return f"{pathobj.parent.name}/{pathobj.name}"
        return path

    def make_session_result(self) -> SessionResult | None:
        if not self._done:
            return None
        return self._result

    def make_session_start(self) -> SessionStart:
        return SessionStart(
            pytest_version=pytest.__version__, plugin_version=__version__
        )

    def make_session_finish(self, exit_status: int) -> SessionFinish:
        self._result.exit_status = exit_status
        self._done = True
        return SessionFinish(exit_status=exit_status)

    def make_warning_message(
        self,
        warning_message: warnings.WarningMessage,
        when: Literal["config", "collect", "runtest"],
        nodeid: str,
    ) -> WarningMessage:
        msg = WarningMessage(
            category=warning_message.category.__name__
            if warning_message.category
            else None,
            location=Location(
                filename=self._get_path(warning_message.filename, True),
                lineno=warning_message.lineno,
            ),
            message=api.make_warning_message(warning_message),
            when=when,  # type: ignore[arg-type],
            node_id=nodeid,
        )
        self._result.warnings.append(msg)
        return msg

    def make_error_message(
        self, report: pytest.CollectReport, call: pytest.CallInfo[Any]
    ) -> ErrorMessage:
        exc_info: pytest.ExceptionInfo[BaseException] | None = call.excinfo
        assert exc_info, "exception info is missing"
        exc_repr = exc_info.getrepr()
        assert exc_repr.reprcrash, "exception crash repr is missing"
        traceback_lines = api.make_traceback_from_reprtraceback(exc_repr.reprtraceback)
        msg = ErrorMessage(
            when=call.when,  # type: ignore[arg-type]
            location=Location(
                filename=self._get_path(exc_repr.reprcrash.path, True),
                lineno=exc_repr.reprcrash.lineno,
            ),
            traceback=Traceback(
                entries=[
                    Entry(
                        lineno=line.lineno,
                        path=line.path,
                        message=line.message,
                    )
                    for line in traceback_lines
                ]
            ),
            exception_type=exc_info.typename,
            exception_value=str(exc_info.value),
        )
        self._result.errors.append(msg)
        return msg

    def make_collect_report(self, report: pytest.CollectReport) -> CollectReport:
        items: list[TestCase | TestDirectory | TestModule | TestSuite] = []  # noqa: F821
        # Format all test items reported
        for result in report.result:
            if isinstance(result, pytest.Directory):
                items.append(
                    TestDirectory(
                        node_id=result.nodeid,
                        name=result.path.name,
                        path=self._get_path(result.path.as_posix()),
                    )
                )
                continue
            if isinstance(result, pytest.Module):
                items.append(
                    TestModule(
                        node_id=result.nodeid,
                        name=result.name,
                        path=self._get_path(result.path.as_posix()),
                        markers=api.field_markers(result),
                        doc=api.field_doc(result),
                    )
                )
                continue
            if isinstance(result, pytest.Class):
                node_id = api.make_node_id(result)
                assert node_id.module
                items.append(
                    TestSuite(
                        node_id=result.nodeid,
                        name=result.name,
                        module=node_id.module,
                        path=self._get_path(result.path.as_posix()),
                        doc=api.field_doc(result),
                        markers=api.field_markers(result),
                    )
                )
                continue
            if isinstance(result, pytest.Function):
                node_id = api.make_node_id(result)
                item = TestCase(
                    node_id=node_id.value,
                    name=node_id.name,
                    module=node_id.module,
                    suite=node_id.suite(),
                    function=node_id.func,
                    path=self._get_path(result.path.as_posix()),
                    doc=api.field_doc(result),
                    markers=api.field_markers(result),
                    parameters=api.field_parameters(result),
                )
                items.append(item)
        # Generate a collect report event.
        collect_report = CollectReport(
            items=items,
            node_id=report.nodeid or "",
        )
        self._result.collect_reports.append(collect_report)
        return collect_report

    def make_test_case_step(
        self, report: pytest.TestReport
    ) -> TestCaseCall | TestCaseSetup | TestCaseTeardown:
        # Always validate the outcome
        outcome = Outcome(report.outcome)
        # Let's process the error if any
        error: TestCaseError | None = None
        if report.failed:
            error = TestCaseError(
                message=report.longreprtext,
                traceback=Traceback(
                    entries=[
                        Entry(path=line.path, lineno=line.lineno, message=line.message)
                        for line in api.make_traceback(report)
                    ]
                ),
            )
        # Let's process the report based on the step
        step: TestCaseSetup | TestCaseCall | TestCaseTeardown
        if report.when == "setup":
            step = TestCaseSetup(
                node_id=report.nodeid,
                outcome=outcome,
                duration=report.duration,
                error=error,
                start=api.make_timestamp(report.start),
                stop=api.make_timestamp(report.stop),
            )
            self._pending_report = TestCaseReport(
                node_id=report.nodeid,
                outcome=outcome,
                duration=step.duration,
                setup=step,
                teardown=...,  # type: ignore (will be set later)
                finished=...,  # type: ignore (will be set later)
            )
        elif report.when == "call":
            if outcome == Outcome.skipped and hasattr(report, "wasxfail"):
                outcome = Outcome.xfailed
            step = TestCaseCall(
                node_id=report.nodeid,
                outcome=outcome,
                duration=report.duration,
                error=error,
                start=api.make_timestamp(report.start),
                stop=api.make_timestamp(report.stop),
            )
            assert (
                self._pending_report
            ), "pending report is missing, this is a bug in pytest-broadcaster plugin"
            self._pending_report.call = step

        elif report.when == "teardown":
            step = TestCaseTeardown(
                node_id=report.nodeid,
                outcome=outcome,
                duration=report.duration,
                error=error,
                start=api.make_timestamp(report.start),
                stop=api.make_timestamp(report.stop),
            )
            assert (
                self._pending_report
            ), "pending report is missing, this is a bug in pytest-broadcaster plugin"
            self._pending_report.teardown = step
        else:
            raise ValueError(f"Unknown step {report.when}")
        return step

    def make_test_case_finished(self, node_id: str) -> TestCaseFinished:
        # Let's pop the pending report (we always have one)
        pending_report = self._pending_report
        self._pending_report = None
        assert (
            pending_report
        ), "pending report is missing, this is a bug in pytest-broadcaster plugin"
        assert (
            pending_report.node_id == node_id
        ), "node_id mismatch, this is a bug in pytest-broadcaster plugin"
        # Get all reports
        reports = [
            report
            for report in (
                pending_report.setup,
                pending_report.call,
                pending_report.teardown,
            )
            if report is not None
        ]
        # Detect if test was failed
        if any(report.outcome == Outcome.failed for report in reports):
            outcome = Outcome.failed
        elif any(report.outcome == Outcome.xfailed for report in reports):
            outcome = Outcome.xfailed
        # Detect if test was skipped
        elif any(report.outcome == Outcome.skipped for report in reports):
            outcome = Outcome.skipped
        # Else consider test passed
        else:
            outcome = Outcome.passed
        duration = sum(report.duration for report in reports)
        # Create the finished event
        finished = TestCaseFinished(
            node_id=node_id,
            outcome=outcome,
            duration=duration,
            start=pending_report.setup.start,
            stop=pending_report.teardown.stop,
        )
        # Create the report
        report = TestCaseReport(
            node_id=node_id,
            outcome=finished.outcome,
            duration=finished.duration,
            finished=finished,
            setup=pending_report.setup,
            call=pending_report.call,
            teardown=pending_report.teardown,
        )
        self._result.test_reports.append(report)
        return finished


if TYPE_CHECKING:
    # Make sure that the class implements the interface
    DefaultReporter()
