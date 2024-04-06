# Streaming JSON to a Webhook

To publish a JSON Lines log stream over HTTP, you can use the `--collect-log-url` option with a URL. This will send a POST request for each [session event][pytest_broadcaster.models.session_event.SessionEvent].


| Option | Description |
|--------|-------------|
| `--collect-log-url` | Send session events to `HTTP` webhook using a `POST` requests. |


<!-- termynal -->

```
$ pytest --collect-log-url=http://localhost:8000
```

A `POST` request is sent for each [event][pytest_broadcaster.models.session_event.SessionEvent] as it occurs during the session.
