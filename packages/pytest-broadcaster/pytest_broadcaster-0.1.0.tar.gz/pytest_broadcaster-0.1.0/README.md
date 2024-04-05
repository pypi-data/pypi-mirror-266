# pytest-broadcaster

A plugin to write pytest collect output to various destinations.

Available destinations:

- JSON file
- JSON lines file.
- HTTP URL (only POST request)

Additional destinations can be added in the future, and users can also implement their own destinations.

## Project state

This project is in early development. The plugin is functional, but the API is not stable yet. The plugin is tested with Python 3.8, 3.9, 3.10, 3.11, and 3.12.

If you find a bug, please open an issue. Contributions are welcome.

## Install

```bash
pip install pytest-broadcaster
```

## Motivation

If you ever wanter to build a tool that needs to parse the output of `pytest --collect-only`, you may have noticed that the output is not very easy to parse. This plugin aims to provide a more structured output that can be easily parsed by other tools.

Historically, this project only parsed the output of `pytest --collect-only`, but it has been extended to parse the output of `pytest` in general.

JSON schemas are provided for clients to help them parse the output of the plugin.

## Usage

- Use the `--collect-report` to generate a JSON file:

```bash
pytest --collect-report=collect.json
```

- Use the `--collect-log` to generate a JSON lines file:

```bash
pytest --collect-log=collect.jsonl
```

- Use the `--collect-url` to send session result to an HTTP URL:

```bash
pytest --collect-url=http://localhost:8000/collect
```

- Use the `--collect-log-url` to send each session event to an HTTP URL:

```bash
pytest --collect-log-url=http://localhost:8000/collect
```

## JSON Schemas

The plugin provides JSON schemas to validate the output of the plugin. Generated schemas are located in the [schemas](./schemas/) directory, while the original schemas are located in the [src/pytest_broadcaster/schemas](./src/pytest_broadcaster/schemas) directory.

### `SessionResult`

The JSON output produced by the plugin follows the [SessionResult JSON Schema](https://github.com/charbonnierg/pytest-broadcaster/tree/main/schemas/session_result.json).

Python tools can also use the [`SessionResult` dataclass](https://github.com/charbonnierg/pytest-broadcaster/tree/main/src/pytest_broadcaster/models/session_result.py) to parse the JSON file.


### `SessionEvent`

The JSON lines output produced by the plugin follows the [SessionEvent JSON Schema](https://github.com/charbonnierg/pytest-broadcaster/tree/main/schemas/session_event.json).

This schema is the union of the different events that can be emitted by the plugin:

- [`SessionStart` JSON Schema](https://github.com/charbonnierg/pytest-broadcaster/tree/main/schemas/session_start.json)
- [`WarningMessage` JSON Schema](https://github.com/charbonnierg/pytest-broadcaster/tree/main/schemas/warning_message.json)
- [`ErrorMessage` JSON Schema](https://github.com/charbonnierg/pytest-broadcaster/tree/main/schemas/error_message.json)
- [`CollectReport` JSON Schema](https://github.com/charbonnierg/pytest-broadcaster/tree/main/schemas/collect_report.json)
- [`TestCaseSetup` JSON Schema](https://github.com/charbonnierg/pytest-broadcaster/tree/main/schemas/test_case_setup.json)
- [`TestCaseCall` JSON Schema](https://github.com/charbonnierg/pytest-broadcaster/tree/main/schemas/test_case_call.json)
- [`TestCaseTeardown` JSON Schema](https://github.com/charbonnierg/pytest-broadcaster/tree/main/schemas/test_case_teardown.json)
- [`TestCaseFinished` JSON Schema](https://github.com/charbonnierg/pytest-broadcaster/tree/main/schemas/test_case_finished.json)
- [`SessionFinish` JSON Schema](https://github.com/charbonnierg/pytest-broadcaster/tree/main/schemas/session_finish.json)

Python tools can also use the [`SessionEvent` dataclass](https://github.com/charbonnierg/pytest-broadcaster/tree/main/src/pytest_broadcaster/models/session_event.py) to parse the JSON lines file, as well as the differnt event classes:

- [`SessionStart` dataclass](https://github.com/charbonnierg/pytest-broadcaster/tree/main/src/pytest_broadcaster/models/session_start.py)
- [`WarningMessage` dataclass](https://github.com/charbonnierg/pytest-broadcaster/tree/main/src/pytest_broadcaster/models/warning_message.py)
- [`ErrorMessage` dataclass](https://github.com/charbonnierg/pytest-broadcaster/tree/main/src/pytest_broadcaster/models/error_message.py)
- [`CollectReport` dataclass](https://github.com/charbonnierg/pytest-broadcaster/tree/main/src/pytest_broadcaster/models/collect_report.py)
- [`TestCaseSetup` dataclass](https://github.com/charbonnierg/pytest-broadcaster/tree/main/src/pytest_broadcaster/models/test_case_setup.py)
- [`TestCaseCall` dataclass](https://github.com/charbonnierg/pytest-broadcaster/tree/main/src/pytest_broadcaster/models/test_case_call.py)
- [`TestCaseTeardown` dataclass](https://github.com/charbonnierg/pytest-broadcaster/tree/main/src/pytest_broadcaster/models/test_case_teardown.py)
- [`TestCaseFinished` dataclass](https://github.com/charbonnierg/pytest-broadcaster/tree/main/src/pytest_broadcaster/models/test_case_finished.py)
- [`SessionFinish` dataclass](https://github.com/charbonnierg/pytest-broadcaster/tree/main/src/pytest_broadcaster/models/session_finish.py)

## Hooks

### `pytest_broadcaster_add_destination`

The plugin provides a hook that can be used by users to add custom destinations. For example, in your `conftest.py` you can add the following code to write the collect output to a JSON file and a JSON lines file:

```python
from pytest_broadcaster import JSONFile, JSONLinesFile


def pytest_broadcaster_add_destination(add):
    add(JSONFile("collect.json"))
    add(JSONLinesFile("collect.jsonl"))
```

### `pytest_broadcaster_set_reporter`

The plugin provides a hook that can be used by users to set a custom reporter. For example, in your `conftest.py` you can add the following code to use a custom reporter (well the default reporter in this case):

```python
from pytest_broadcaster import DefaultReporter


def pytest_broadcaster_set_reporter(set):
    set(DefaultReporter())
```

## Alternatives

- [pytest-json-report](https://github.com/numirias/pytest-json-report): This plugin predates `pytest-broadcaster`, has been used by several organizations, and works well. However, there is no JSON schema to validate the output, nor JSON lines output. Also, it does not allow adding custom destinations as `pytest-broadcaster` does.

- [pytest-report-log](https://github.com/pytest-dev/pytest-reportlog): This package provides both JSON and JSON lines output, but it does not provide a JSON schema to validate the output. Also, it does not allow adding custom destinations as `pytest-broadcaster` does.

## Credits

- [pytest](https://docs.pytest.org/en/8.0.x/): Well, this is a pytest plugin.
- [pytest-report-log](https://github.com/pytest-dev/pytest-reportlog): This package was heavily inspired by the `report-log` plugin.
- [pytest-json-report](https://github.com/numirias/pytest-json-report): The `pytest-json-report` plugin was also a source of inspiration.
- [pytest-csv](https://github.com/nicoulaj/pytest-csv): The `pytest-csv` plugin was also a source of inspiration.
- [`datamodel-code-generator`](https://github.com/koxudaxi/datamodel-code-generator): The dataclasses generation from JSON schemas is performed using `datamodel-code-generator`.
- [rye](https://rye-up.com/): Project management is easy thanks to `rye`. It is also used to lint and format the code.
- [hatch-vcs](https://github.com/ofek/hatch-vcs): Python project version control is easy thanks to `hatch-vcs`.
- [pyright](https://github.com/microsoft/pyright): `pyright` is used to check the code and find bugs sooner.

## License

This project is licensed under the terms of the MIT license. See [LICENSE](./LICENSE) for more information.
