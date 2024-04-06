# Sending JSON to a Webhook

To publish a JSON report over HTTP, you can use the `--collect-url` option with a URL. This will send a POST request with the [session result][pytest_broadcaster.models.session_result.SessionResult].


| Option | Description |
|--------|-------------|
| `--collect-url` | Send a JSON report file with the session result to a `HTTP` webhook using a `POST` request. |

<!-- termynal -->

```
$ pytest --collect-url=http://localhost:8000
```

The `POST` request is sent on session exit, after all tests have been collected and run.
