# Generating a JSON report

To generate a JSON report, you can use the `--collect-report` option with a filename. This will output a JSON file with the [session result][pytest_broadcaster.models.session_result.SessionResult].

| Option | Description |
|--------|-------------|
| `--collect-report` | Output a JSON report file with the session result. |


<!-- termynal -->

```
$ pytest --collect-report=report.json
```

The report will be written on session exit, after all tests have been collected and run.
