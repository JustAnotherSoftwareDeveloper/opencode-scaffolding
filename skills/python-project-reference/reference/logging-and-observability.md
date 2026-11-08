# Logging And Observability

## Follow A Record Through The Pipeline

Python logging creates `LogRecord` objects. Loggers, filters, handlers, and formatters
determine whether a record is processed, where it goes, and how it is rendered. A
module-named logger can propagate to ancestor handlers; attaching handlers at both a
child and its root can emit one event more than once. `extra` adds attributes to a
record, but does not itself serialize JSON or guarantee that a chosen formatter keeps
those fields. ([Python 3.15.2 logging](https://docs.python.org/3.15/library/logging.html).)

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
this shape. `json.dumps` also requires values that it can encode. ([Python 3.15.2
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

Check logger and handler thresholds separately. A logger may accept an `INFO` record
that its handler discards at `WARNING`; changing the formatter cannot recover a record
filtered out earlier. Python's levels describe the event, not a paging policy:

- `DEBUG`: detailed diagnostic information.
- `INFO`: expected operation or a useful completed outcome.
- `WARNING`: unexpected or potentially problematic behavior while work continues.
- `ERROR`: a failure prevented some requested function from completing.
- `CRITICAL`: a serious failure may prevent the program from continuing.

The default root threshold is `WARNING`, not a recommended universal production level.
Choose operational alerts separately from code-level severity. An expected validation
rejection, a recovered retry, and a failed user operation need not share a level. See
the [Logging HOWTO](https://docs.python.org/3.15/howto/logging.html#when-to-use-logging).

`extra` keys must not collide with reserved `LogRecord` attributes such as `name` or
`message`. Conversely, a formatter using `%(request_id)s` can fail on records that
lack that field. The custom formatter above uses `getattr(..., None)` deliberately;
a logging adapter or filter is another place to establish a consistent field contract.
Test both contextual and context-free records, not just the happy-path event.

Use interaction/request IDs only for their intended diagnostic context; they are not
trace/span IDs or authorization evidence. `contextvars` supports context-local values
and token-based restoration in Python 3.15.2, but does not prove propagation through
every thread, process, network, or instrumentation boundary. Verify the target
execution model. ([Python 3.15.2 `contextvars`](https://docs.python.org/3.15/library/contextvars.html).)

## Scope Context So One Request Does Not Inherit Another

Use a reset token to restore the previous context even if request handling raises:

```python
from contextvars import ContextVar

request_id = ContextVar("request_id", default=None)


def handle_request(identifier, action):
    token = request_id.set(identifier)
    try:
        return action()
    finally:
        request_id.reset(token)
```

Assumptions: `identifier` is safe diagnostic context and `action` is a synchronous
callable. The token restores a prior nested value, not just an empty default. The
same `try/finally` principle applies across an awaited request lifetime. A formatter,
filter, or adapter must still read and attach the value; setting a ContextVar alone
does not add a log field or send it over HTTP. Python's
[logging cookbook](https://docs.python.org/3.15/howto/logging-cookbook.html#use-of-contextvars)
shows context integration; verify thread/executor/process propagation in the actual
execution model rather than assuming a universal transport.

## Report Handled Failures Without Replacing Error Control Flow

Raise an error that the caller must handle. When the current boundary handles a
failure and traceback evidence is useful, `logger.exception()` emits an `ERROR` record
with exception information from inside the handler. Calling it outside an exception
handler does not recover some earlier failure. Other levels can attach `exc_info`
when appropriate.

```python
try:
    result = refresh_catalog()
except CatalogUnavailable:
    logger.exception("catalog.refresh_failed")
    result = cached_catalog()
```

This hypothetical boundary deliberately selects a cached fallback. The log does not
turn a failed refresh into a successful one. If the public contract requires failure
propagation instead, a fallback would be incorrect. Review the exception's own message
and traceback for sensitive values before emitting it; a constant event name cannot
sanitize attached exception details. Reporting once at the handling boundary can avoid
duplicate stack traces at every re-raise, but existing logging contracts control that
choice ([Python exception logging](https://docs.python.org/3.15/howto/logging.html#exceptions-raised-during-logging)).

## Encode Untrusted Fields Without Losing The Event

An interaction identifier or user field can contain delimiters, carriage returns,
newlines, or attacker-controlled text. Validate its shape and bound its length before
emission; encode it for the chosen output format. JSON encoding escapes embedded
newlines inside a string, whereas concatenating the same raw value into a line-based
format can forge an apparent second event. The encoding must happen in the actual
handler/formatter route, including fallback error paths.

When a field is invalid, omit it or replace it with safe bounded context while retaining
the useful security event. Do not log the entire rejected payload as the validation
error. Sensitive-data inclusion and masking decisions belong to
[Secure Configuration And Data Handling](secure-configuration-and-data-handling.md);
[OWASP's event-collection guidance](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html#event-collection)
explains the injection and output-encoding concern.

## Distinguish Interaction Context From Distributed Traces

A request/interaction ID can link application events without defining a distributed
trace. A trace ID identifies the trace and a span ID identifies one position within
it; a span ID without its trace ID loses that association. W3C Trace Context defines
HTTP `traceparent` and optional `tracestate` for propagation, not automatic Python log
injection or an authentication claim ([Trace Context v1 Recommendation](https://www.w3.org/TR/trace-context/)).
The inspected November 2026 records identified v1 as a Recommendation and Level 2 as
a draft; do not infer finalized requirements from that draft's additions
([Level 2 status](https://www.w3.org/TR/trace-context-2/)).

OpenTelemetry's logical log model also separates event timestamp from observed
timestamp, severity text from a normalized severity number, event body/attributes from
resource identity, and optional trace context. These distinctions help when translating
an existing schema: a service name belongs to the emitting resource, while an order ID
describes one event. A bridge cannot preserve information the original format omitted.
The [log data model](https://opentelemetry.io/docs/specs/otel/logs/data-model/) was marked
stable in the recorded source; that does not make every Python SDK/exporter API stable.
The [Python integration documentation](https://opentelemetry.io/docs/languages/python/instrumentation/)
then marked Logs API/SDK work as under development. Check the selected integration
version before adopting its examples, and do not install telemetry infrastructure just
to emit a structured stdlib record.

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
