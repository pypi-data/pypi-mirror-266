# Generating a JSON Lines log stream


To generate a JSON Lines log stream, you can use the `--collect-log` option with a filename. This will output a JSON Lines stream with the [session events][pytest_broadcaster.models.session_event.SessionEvent].

| Option | Description |
|--------|-------------|
| `--collect-log` | Output session events to JSON Lines file. |

<!-- termynal -->

```
$ pytest --collect-log=events.log
```

The log stream is written as events occur during the session.
