from __future__ import annotations

import warnings
from contextlib import ExitStack
from typing import Any, Literal

import pytest
from _pytest.terminal import TerminalReporter

from pytest_broadcaster import hooks
from pytest_broadcaster._internal._json_files import JSONFile, JSONLinesFile
from pytest_broadcaster._internal._reporter import DefaultReporter
from pytest_broadcaster._internal._webhook import HTTPWebhook
from pytest_broadcaster.interfaces import Destination, Reporter
from pytest_broadcaster.models.session_event import SessionEvent
from pytest_broadcaster.models.session_result import SessionResult

__PLUGIN_ATTR__ = "_broadcaster_plugin"


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register argparse-style options and ini-style config values.

    This function is called once at the beginning of a test run.

    Performs the following action:

    - Get or create the `terminal reporting` group in the parser.
    - Add the `--collect-report` option to the group.
    - Add the `--collect-log` option to the group.
    - Add the `--collect-url` option to the group.
    - Add the `--collect-log-url` option to the group.

    See [pytest.hookspec.pytest_addoption][_pytest.hookspec.pytest_addoption].
    """
    group = parser.getgroup(
        name="terminal reporting",
        description="pytest-broadcaster plugin options",
    )
    group.addoption(
        "--collect-report",
        action="store",
        metavar="path",
        default=None,
        help="Path to JSON output file holding collected items.",
    )
    group.addoption(
        "--collect-log",
        action="store",
        metavar="path",
        default=None,
        help="Path to JSON Lines output file where events are logged to.",
    )
    group.addoption(
        "--collect-url",
        action="store",
        metavar="url",
        default=None,
        help="URL to send collected items to.",
    )
    group.addoption(
        "--collect-log-url",
        action="store",
        metavar="url",
        default=None,
        help="URL to send events to.",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Perform initial plugin configuration.

    This function is called once after command line options have been parsed.

    Performs the following actions:

    - Skip if workerinput is present, which means we are in a worker process.
    - Create a JSONFile destination if the JSON output file path is present.
    - Create a JSONLinesFile destination if the JSON Lines output file path is present.
    - Create an HTTPWebhook destination if the URL is present.
    - Create an HTTPWebhook destination if the URL for the JSON Lines output file is present.
    - Let the user add their own destinations if they want to.
    - Create the default reporter.
    - Let the user set the reporter if they want to.
    - Create, open and register the plugin instance.
    - Store the plugin instance in the config object.

    See [pytest.hookspec.pytest_configure][_pytest.hookspec.pytest_configure].
    """
    # Skip if pytest-xdist worker
    if hasattr(config, "workerinput"):
        return

    # Create publishers
    destinations: list[Destination] = []

    if json_path := config.option.collect_report:
        destinations.append(JSONFile(json_path))

    if json_lines_path := config.option.collect_log:
        destinations.append(JSONLinesFile(json_lines_path))

    if json_url := config.option.collect_url:
        destinations.append(HTTPWebhook(json_url, emit_events=False, emit_result=True))

    if json_lines_url := config.option.collect_log_url:
        destinations.append(
            HTTPWebhook(json_lines_url, emit_events=True, emit_result=False)
        )

    def add_destination(destination: Destination) -> None:
        destinations.append(destination)

    # Let the user add their own destinations if they want to
    config.hook.pytest_broadcaster_add_destination(add=add_destination)

    # Create default reporter
    reporter_to_use = DefaultReporter()

    def set_reporter(reporter: Reporter) -> None:
        nonlocal reporter_to_use
        reporter_to_use = reporter

    # Let the user set the reporter if they want to
    config.hook.pytest_broadcaster_set_reporter(set=set_reporter)

    # Create plugin instance.
    plugin = PytestBroadcasterPlugin(
        config=config,
        reporter=reporter_to_use,
        publishers=destinations,
    )
    # Open the plugin
    plugin.open()
    # Register the plugin with the plugin manager.
    config.pluginmanager.register(plugin)
    setattr(config, __PLUGIN_ATTR__, plugin)


def pytest_addhooks(pluginmanager: pytest.PytestPluginManager) -> None:
    """Called at plugin registration time to allow adding new hooks via a call to [pytest.pluginmanager.add_hookspecs][_pytest.pluginmanager.add_hookspecs].

    See [pytest.hookspec.pytest_addhooks][_pytest.hookspec.pytest_addhooks].

    Add the plugin hooks to the plugin manager:

    - [pytest_broadcaster_add_destination][pytest_broadcaster.hooks.pytest_broadcaster_add_destination]: Add a destination to the plugin.
    - [pytest_broadcaster_set_reporter][pytest_broadcaster.hooks.pytest_broadcaster_set_reporter]: Set the reporter to use.
    """
    pluginmanager.add_hookspecs(hooks)


def pytest_unconfigure(config: pytest.Config) -> None:
    """Perform final plugin teardown.

    This function is called once after all test are executed and before test process is exited.

    See [pytest.hookspec.pytest_unconfigure][_pytest.hookspec.pytest_unconfigure].

    Performs the following actions:

    - Extract the plugin instance from the config object.
    - Close the plugin instance.
    - Delete the plugin instance from the config object.
    """
    plugin: PytestBroadcasterPlugin | None = getattr(config, __PLUGIN_ATTR__, None)
    if plugin:
        plugin.close()
        config.pluginmanager.unregister(plugin)
        delattr(config, __PLUGIN_ATTR__)


class PytestBroadcasterPlugin:
    """A pytest plugin to log collection to a line-based JSON file."""

    def __init__(
        self,
        config: pytest.Config,
        reporter: Reporter,
        publishers: list[Destination],
    ) -> None:
        self.config = config
        self.publishers = publishers
        self.reporter = reporter
        self.stack = ExitStack()

    def open(self) -> None:
        """Open the plugin instance. It performs the following actions:

        - Skip if there is no JSON Lines output
        - Raise an error if the JSON Lines output file is already open.
        - Ensure the parent directory of JSON Lines output file exists.
        - Open the JSON Lines output file in write mode (erasing any previous content)
        """
        for publisher in self.publishers:
            try:
                self.stack.enter_context(publisher)
            except Exception as e:
                warnings.warn(f"Failed to open publisher: {publisher} - {repr(e)}")

    def close(self) -> None:
        """Close the plugin instance. It performs the following actions:

        - Close the JSON Lines output file (if any).
        - Write the results to the JSON output file (if any)
        """
        if result := self.reporter.make_session_result():
            self._write_result(result)
        self.stack.close()

    def pytest_sessionstart(self) -> None:
        """Called after the [Session object][pytest.Session] has been created and before performing collection and entering the run test loop.

        See [pytest.hookspec.pytest_sessionstart][_pytest.hookspec.pytest_sessionstart].
        """
        self._write_event(self.reporter.make_session_start())

    def pytest_sessionfinish(self, exitstatus: int) -> None:
        """Called after whole test run finished, right before returning the exit status to the system.

        See [pytest.hookspec.pytest_sessionfinish][_pytest.hookspec.pytest_sessionfinish].
        """
        self._write_event(self.reporter.make_session_finish(exitstatus))

    def pytest_warning_recorded(
        self,
        warning_message: warnings.WarningMessage,
        when: Literal["config", "collect", "runtest"],
        nodeid: str,
        location: tuple[str, int, str] | None,
    ):
        """Process a warning captured during the session.

        See [pytest.hookspec.pytest_warning_recorded][_pytest.hookspec.pytest_warning_recorded].
        """
        self._write_event(
            self.reporter.make_warning_message(
                warning_message=warning_message,
                when=when,
                nodeid=nodeid,
            )
        )

    def pytest_exception_interact(
        self,
        node: pytest.Item | pytest.Collector,
        call: pytest.CallInfo[Any],
        report: pytest.TestReport | pytest.CollectReport,
    ) -> None:
        """Collector encountered an error.

        See [pytest.hookspec.pytest_exception_interact][_pytest.hookspec.pytest_exception_interact].
        """
        # Skip if the report is not a test report.
        if isinstance(report, pytest.TestReport):
            return
        self._write_event(self.reporter.make_error_message(report, call))

    def pytest_collectreport(self, report: pytest.CollectReport) -> None:
        """Collector finished collecting a node.

        See [pytest.hookspec.pytest_collectreport][_pytest.hookspec.pytest_collectreport].
        """
        # Skip if the report failed.
        if report.failed:
            return
        self._write_event(self.reporter.make_collect_report(report))

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        """Process the [TestReport][pytest.TestReport] produced for each of the setup, call and teardown runtest steps of a test case.

        See [pytest.hookspec.pytest_runtest_logreport][_pytest.hookspec.pytest_runtest_logreport].
        """
        self._write_event(self.reporter.make_test_case_step(report))

    def pytest_runtest_logfinish(
        self, nodeid: str, location: tuple[str, int | None, str]
    ) -> None:
        """Called at the end of running the runtest protocol for a single item.

        See [pytest.hookspec.pytest_runtest_logfinish][_pytest.hookspec.pytest_runtest_logfinish].
        """
        self._write_event(self.reporter.make_test_case_finished(nodeid))

    def pytest_terminal_summary(self, terminalreporter: TerminalReporter):
        """Add a section to terminal summary reporting.

        See [pytest.hookspec.pytest_terminal_summary][_pytest.hookspec.pytest_terminal_summary].
        """
        for publisher in self.publishers:
            if summary := publisher.summary():
                terminalreporter.write_sep("-", f"generated report log file: {summary}")

    def _write_event(self, event: SessionEvent) -> None:
        """Write a session event to the destinations."""
        for publisher in self.publishers:
            try:
                publisher.write_event(event)
            except Exception as e:
                warnings.warn(
                    f"Failed to write event to destination: {publisher} - {repr(e)}"
                )

    def _write_result(self, result: SessionResult) -> None:
        """Write the session result to the destinations."""
        for publisher in self.publishers:
            try:
                publisher.write_result(result)
            except Exception as e:
                warnings.warn(
                    f"Failed to write result to destination: {publisher} - {repr(e)}",
                )
