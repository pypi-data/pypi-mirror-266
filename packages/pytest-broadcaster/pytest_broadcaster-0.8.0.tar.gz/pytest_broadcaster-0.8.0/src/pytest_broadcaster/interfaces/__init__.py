from __future__ import annotations

import abc
import warnings
from typing import Any, Literal

import pytest

from ..models.collect_report import CollectReport
from ..models.error_message import ErrorMessage
from ..models.session_event import SessionEvent
from ..models.session_finish import SessionFinish
from ..models.session_result import SessionResult
from ..models.session_start import SessionStart
from ..models.test_case_call import TestCaseCall
from ..models.test_case_finished import TestCaseFinished
from ..models.test_case_setup import TestCaseSetup
from ..models.test_case_teardown import TestCaseTeardown
from ..models.warning_message import WarningMessage


class Destination(metaclass=abc.ABCMeta):
    """An interface where you can write events and results."""

    @abc.abstractmethod
    def write_event(self, event: SessionEvent) -> None:
        """Write an event to the destination."""

    @abc.abstractmethod
    def write_result(self, result: SessionResult) -> None:
        """Write the session result to the destination."""

    @abc.abstractmethod
    def summary(self) -> str | None:
        """Return a summary of the destination."""

    def open(self) -> None:
        """Open the destination. No-op by default."""

    def close(self) -> None:
        """Close the destination. No-op by default."""

    def __enter__(self) -> Destination:
        self.open()
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.close()


class Reporter(metaclass=abc.ABCMeta):
    """An interface to create events and results."""

    @abc.abstractmethod
    def make_session_result(self) -> SessionResult | None:
        """Return the session result, if session is done, else returns None."""

    @abc.abstractmethod
    def make_session_start(self) -> SessionStart:
        """Return a session start event."""

    @abc.abstractmethod
    def make_session_finish(self, exit_status: int) -> SessionFinish:
        """Return a session finish event."""

    @abc.abstractmethod
    def make_warning_message(
        self,
        warning_message: warnings.WarningMessage,
        when: Literal["config", "collect", "runtest"],
        nodeid: str,
    ) -> WarningMessage:
        """Return a warning message event."""

    @abc.abstractmethod
    def make_error_message(
        self, report: pytest.CollectReport, call: pytest.CallInfo[Any]
    ) -> ErrorMessage:
        """Return an error message event."""

    @abc.abstractmethod
    def make_collect_report(self, report: pytest.CollectReport) -> CollectReport:
        """Return a collect report event."""

    @abc.abstractmethod
    def make_test_case_step(
        self, report: pytest.TestReport
    ) -> TestCaseCall | TestCaseSetup | TestCaseTeardown:
        """Return a test case step event."""

    @abc.abstractmethod
    def make_test_case_finished(self, node_id: str) -> TestCaseFinished:
        """Return a test case finished event."""
