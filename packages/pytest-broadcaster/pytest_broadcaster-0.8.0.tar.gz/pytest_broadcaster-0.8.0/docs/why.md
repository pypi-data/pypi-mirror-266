# Why another plugin ?

If you ever wanter to build a tool that needs to parse the output of `pytest`, you may have noticed that the output is not very easy to parse.

The page [Managing pytest's output](https://docs.pytest.org/en/7.1.x/how-to/output.html) describes the different output formats of `pytest`, and how to use them.

## Built-in solutions

The built-in solutions are:

- [Creating resultlog format files](https://docs.pytest.org/en/7.1.x/how-to/output.html#creating-resultlog-format-files): `pytest --resultlog=path`. However, the format is not easy to parse, and this option has [been removed in version 6.0](https://docs.pytest.org/en/7.1.x/deprecations.html#resultlog-deprecated).

- [Creating JUnitXML format files](https://docs.pytest.org/en/7.1.x/how-to/output.html#creating-junitxml-format-files): `pytest --junitxml=path`. This format is easier to parse, but does not contain all the information that `pytest` outputs. Also, I'm not aware of a XML schema for the output of `pytest`, and using user properties will break the validation schema used by some CI servers. Instead, it is recommended to use [`record-xml-attribute`](https://docs.pytest.org/en/7.1.x/how-to/output.html#record-xml-attribute).

And that's it. There is no built-in solution to get a structured output of `pytest` other than JUnit that can be easily parsed by other tools.

## Plugins

There are plugins however, that can help you parse the output of `pytest`:

- [`pytest-reportlog`](https://github.com/pytest-dev/pytest-reportlog): Replacement for the --resultlog option, focused in simplicity and extensibility.

- [`pytest-json-report`](https://github.com/numirias/pytest-json-report): A pytest plugin to report test results in JSON format.

- [`pytest-csv`](https://github.com/nicoulaj/pytest-csv): A pytest plugin to report test results in CSV format.

## Shortcomings of plugins

The plugins above are great, but:

- `pytest-reportlog` is focused on test result and omits the collection phase. It also does not provide JSON schemas to parse the output in other languages.

- `pytest-json-report` is powerful, but can only write to files, and does not provide JSON schemas to parse the output in other languages.

- `pytest-csv` is also powerful, especially in reporting meaningful information, but it can be tedious to parse reports from other languages.

## `pytest-broadcaster`	

This plugin aims to provide a more structured output that can be easily parsed by other tools.

It does not aim to limit users with a single output destination (e.g., JSON file, JSON Lines file, HTTP Webhook), but to provide a flexible way to output the data to various destinations.

JSON schemas are also provided for clients to help them parse the output of the plugin.

The fact that this plugin works in two phase:

- reporting
- emitting

allows it to be more flexible in the way it can be used.

The fact that it provides JSON Schema for the output allows it to generate code in other languages to parse the output of the plugin.
