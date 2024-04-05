# Plugin Options

## Generating a JSON report

To generate a JSON report, you can use the `--collect-report` option with a filename. This will output a JSON file with the [session result][pytest_broadcaster.models.session_result.SessionResult].

<!-- termynal -->

```
$ pytest --collect-report=report.json
```

The report will be written on session exit, after all tests have been collected and run.

## Generating a JSON Lines log stream


To generate a JSON Lines log stream, you can use the `--collect-log` option with a filename. This will output a JSON Lines stream with the [session events][pytest_broadcaster.models.session_event.SessionEvent].

<!-- termynal -->

```
$ pytest --collect-log=events.log
```

The log stream is written as events occur during the session.

## Publishing a JSON report over HTTP

To publish a JSON report over HTTP, you can use the `--collect-url` option with a URL. This will send a POST request with the [session result][pytest_broadcaster.models.session_result.SessionResult].

<!-- termynal -->

```
$ pytest --collect-url=http://localhost:8000
```

The `POST` request is sent on session exit, after all tests have been collected and run.

## Publishing a JSON Lines log stream over HTTP

To publish a JSON Lines log stream over HTTP, you can use the `--collect-log-url` option with a URL. This will send a POST request for each [session event][pytest_broadcaster.models.session_event.SessionEvent].

<!-- termynal -->

```
$ pytest --collect-log-url=http://localhost:8000
```

A `POST` request is sent for each [event][pytest_broadcaster.models.session_event.SessionEvent] as it occurs during the session.
