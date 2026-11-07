# Logging And Observability

## Follow A Record Through The Pipeline

Python logging creates `LogRecord` objects. Loggers, filters, handlers, and formatters
determine whether a record is processed, where it goes, and how it is rendered. A
module-named logger can propagate to ancestor handlers; attaching handlers at both a
child and its root can emit one event more than once. `extra` adds attributes to a
record, but does not itself serialize JSON or guarantee that a chosen formatter keeps
those fields. (Dossier C18-C19, C30; [Python 3.15.2 logging](https://docs.python.org/3.15/library/logging.html).)

This standard-library example chooses a small formatter explicitly:

```python
import json
import logging


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "request_id": getattr(record, "request_id", None),
            }
        )


logger = logging.getLogger("example.worker")
logger.setLevel(logging.INFO)
logger.propagate = False
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.info("checkout.completed", extra={"request_id": "r-7"})
```

Assumptions: this illustrative logger has one handler, and the example's request ID is
non-sensitive. By construction, the formatter serializes the selected level, logger,
message, and request ID fields; other `extra` values are omitted. It does not establish
a universal schema or redaction policy. Re-running handler setup in a long-lived
process can attach another handler, so inspect existing configuration before applying
this shape. `json.dumps` also requires values that it can encode. (C30; [Python 3.15.2
JSON documentation](https://docs.python.org/3.15/library/json.html).)

## Diagnose Duplicates And Missing Fields

If one event appears twice, trace the child logger's handlers and its ancestor/root
handlers, then inspect propagation. A common correction is to configure handlers at one
deliberate boundary or set a deliberate propagation boundary; avoid adding another
handler before identifying the route.

If a custom field is missing from JSON, inspect both sides: whether the caller supplied
it in `extra`, and whether the formatter explicitly selected and encoded it. The
presence of a `LogRecord` attribute is not proof that a formatter or exporter includes
it. The code above makes its expected field set visible without claiming it has been
run against any application.

Use interaction/request IDs only for their intended diagnostic context; they are not
trace/span IDs or authorization evidence. `contextvars` supports context-local values
and token-based restoration in Python 3.15.2, but does not prove propagation through
every thread, process, network, or instrumentation boundary. Verify the target
execution model. (C19; [Python 3.15.2 `contextvars`](https://docs.python.org/3.15/library/contextvars.html).)

## Brownfield And Ownership

Reusable libraries normally use named loggers and leave handler setup to applications.
An established service may already have a schema, formatter, collector, trace context,
and alert mapping; preserve those contracts when changing one event. Python levels are
semantic labels, not paging rules or an SLO. Logging an exception is not a substitute
for propagating or translating the failure; that contract belongs to [Source and
API](source-and-api.md). Whether a value may be emitted belongs to [Secure
Configuration and Data Handling](secure-configuration-and-data-handling.md).

The examples are scoped to Python 3.15.2 documentation. The sources do not define a
stock JSON schema, exporter, retention, alert thresholds, or platform controls. No
target logger tree or formatter was inspected.
