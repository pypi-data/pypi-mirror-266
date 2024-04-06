from __future__ import annotations

from typing import Callable

from ..interfaces import Destination, Reporter


def pytest_broadcaster_add_destination(add: Callable[[Destination], None]) -> None:
    """
    Called on plugin initialization.

    Use it to add your own destination.

    For instance, in `conftest.py`:

    ```python
    from pytest_broadcaster import HTTPWebhook

    def pytest_broadcaster_add_destination(add):
        add(HTTPWebhook(url="https://example.com"))
        add(HTTPWebhook(url="https://another-example.com"))
    ```

    Then run pytest without any option:

    ```bash
    pytest
    ```
    """


def pytest_broadcaster_set_reporter(set: Callable[[Reporter], None]) -> None:
    """
    Called on plugin initialization.

    Use it to set your own reporter.

    For instance, in `conftest.py`:

    ```python
    def pytest_broadcaster_set_reporter(set_reporter):
        set(MyReporter())
    ```

    Then run pytest without any option:

    ```bash
    pytest
    ```
    """
