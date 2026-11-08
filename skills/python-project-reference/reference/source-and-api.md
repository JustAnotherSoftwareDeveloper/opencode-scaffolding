# Source And API

## Define The Promise Callers Can Observe

For an API decision, name what a consumer can rely on: supported import path and
symbol, accepted arguments, return behavior, side effects, documented exceptions, and
subclass or override behavior when promised. PEP 387 uses these as compatibility
dimensions for CPython; it is an example, not a third-party project's policy. A version
string accepted by PEP 440 does not define an API lifecycle. ([PEP 387](https://peps.python.org/pep-0387/).)

Annotations and stubs can be part of a typed-client promise if the project advertises
them, but annotations alone do not validate runtime values. Keep three questions
separate: what the runtime accepts, what the static checker accepts, and what the
project promises consumers. General annotation style belongs to
`python-source-style-guide -> reference/python-source-style-guide.md`; checker setup
belongs to [Static Quality](static-quality.md).

For a new library, write down supported import paths and caller-visible failure
outcomes before selecting a deprecation schedule. In a brownfield package, preserve
existing consumer expectations and the actual release policy; do not infer a removal
date from CPython, SemVer, or the current version number.

## Test Runtime And Typed Consumers Separately

An annotation change can break checked clients without changing executable code.
Suppose a public function previously accepted `str | None`. Narrowing its parameter
to `str` rejects a previously valid checked call with `None`, even if the implementation
still handles it. Widening a return from `str` to `str | None` can similarly make
previously checked string operations unsafe. Runtime frameworks that inspect
annotations add another compatibility surface.

A small client example can express the promised static result:

```python
from typing import assert_type

from acme_catalog import lookup_label


def display_label(key: str) -> str:
    label = lookup_label(key)
    assert_type(label, str)
    return label.upper()
```

Assumption: this hypothetical library promises a string result. A selected checker
can diagnose a changed `str | None` return at both the directive and `.upper()` use.
`assert_type` is a checker directive, not runtime validation; record the checker/version
and tested client examples. Its stdlib form requires Python 3.11+; older supported
interpreters may use a compatible `typing_extensions` release, where it was introduced
in 4.2.0. Checker representations of equivalent types can differ. See the
[typing directives](https://typing.python.org/en/latest/spec/directives.html),
[annotation specification](https://typing.python.org/en/latest/spec/annotations.html),
and [typing_extensions compatibility](https://typing-extensions.readthedocs.io/en/latest/).

For runtime compatibility, retain representative old imports, positional/keyword
calls, return/error cases, side effects, and subclass behavior where promised. Test
the installed consumer surface when packaging matters. An unavailable interpreter
that was skipped is an untested target, not a successful compatibility case; pytest's
[cross-interpreter example](https://docs.pytest.org/en/stable/example/parametrize.html)
illustrates that distinction. No suite proves every unobserved consumer use.

## Make Deprecation Observable And Actionable

A deprecation needs a replacement or migration path, a warning/documentation strategy,
a period of retained behavior, and an eventual removal decision. Those are separate
choices. Pallets explicitly disclaims SemVer guarantees; pandas retains deprecated
features for at least two minor releases under its own policy. Neither governs another
project ([Pallets version policy](https://www.palletsprojects.com/versions),
[pandas deprecation policy](https://pandas.pydata.org/pdeps/0017-backwards-compatibility-and-deprecation-policy.html)).
The [baseline's release-policy example](project-baseline-and-adoption.md#public-contracts-and-distribution)
is another proposed choice, not a minimum imposed by Python.

For example, an old callable can retain behavior while directing callers to its successor:

```python
import warnings


def old_label(key):
    warnings.warn(
        "old_label is deprecated; use lookup_label",
        DeprecationWarning,
        stacklevel=2,
    )
    return lookup_label(key)
```

The replacement must actually preserve the promised old behavior for this adapter to
be compatible. `stacklevel=2` points at the caller, but warning filters still control
visibility: `DeprecationWarning` is normally ignored except in `__main__`. A test
should explicitly capture the category/message and exercise the retained result,
rather than assuming users saw the warning. Python 3.13+ also supplies
`warnings.deprecated` for runtime/static signaling; checker support and configuration
remain separate. See [Python warnings](https://docs.python.org/3.15/library/warnings.html).

## Diagnose A Timed-Out Request Before Retrying

A timeout after sending a write does not tell the caller whether the server applied the
effect. RFC 9110 permits automatic retry of a non-idempotent request only when its
semantics are known idempotent or the client can determine the original was not
applied. The endpoint's contract—not the method name or a Python client's default—must
establish replay safety. ([RFC 9110 §9.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2).)

The following urllib3 2.6.3 fragment is an illustrative GET-only client policy. It
limits retries by category; it is not a recommendation for an unknown endpoint:

```python
from urllib3 import PoolManager
from urllib3.util import Retry, Timeout

retry = Retry(
    total=2,
    connect=2,
    read=0,
    status=0,
    allowed_methods=frozenset({"GET"}),
)
timeout = Timeout(connect=2.0, read=5.0)
http = PoolManager(retries=retry, timeout=timeout)
```

With urllib3 2.6.3, connect errors are treated as occurring before the request was
sent, while read errors can occur after it was sent and after side effects. Here read
retries are set to zero. `read` and `total` timeout values measure intervals between
socket reads, not a hard wall-clock limit for the complete response; periodic response
bytes can extend total elapsed time. No call is made by this example. ([urllib3
2.6.3 retry and timeout reference](https://urllib3.readthedocs.io/en/2.6.3/reference/urllib3.util.html).)

When a write acknowledgement is uncertain, the safer alternatives are to avoid blind
replay, consult the endpoint's idempotency/deduplication contract, or reconcile the
operation's state through a supported read path. Do not invent an idempotency-key
contract or assume an SDK retry setting proves one exists. A request-wide deadline is
also different from a per-call/socket timeout; compose one only when the client APIs
support the intended scope.

## Carry One Remaining Budget Across Calls

Giving each layer a fresh full timeout can multiply the caller's intended waiting
budget. A monotonic deadline instead tracks how much remains:

```python
from time import monotonic


def run_with_budget(operations, budget_seconds):
    deadline = monotonic() + budget_seconds
    for operation in operations:
        remaining = deadline - monotonic()
        if remaining <= 0:
            raise TimeoutError("operation budget exhausted")
        operation(timeout=remaining)
```

Assumptions: each supplied callable accepts a seconds-based timeout and its actual
timeout semantics have been checked. The example prevents starting the next call
after the budget is exhausted; it cannot forcibly interrupt a call whose API does not
honor that scope. A socket read timeout, DNS lookup, cleanup, or running worker can
still outlive the intended budget. Choose the budget from the project's latency
contract, not this example. `monotonic()` is unaffected by wall-clock changes; its
undefined reference point means differences, not absolute timestamps, are meaningful
([Python monotonic clock](https://docs.python.org/3.15/library/time.html#time.monotonic)).

Async timeout APIs have different aftermaths in the documented Python 3.15 behavior:

- `asyncio.timeout()` cancels the current task and translates that cancellation into
  `TimeoutError` outside its context. The scope requires Python 3.11+.
- `wait_for()` cancels its awaited object and waits for cancellation to finish, so
  elapsed time can exceed the configured timeout.
- `wait()` returns unfinished tasks as pending on timeout; it neither cancels them
  nor raises `TimeoutError`. The caller still owns their outcomes and lifetime.

Swallowed cancellation or blocked event-loop code can defeat cooperative timeout
behavior. See [asyncio timeout APIs](https://docs.python.org/3.15/library/asyncio-task.html#timeouts)
and [Async And Concurrency](async-and-concurrency.md) for task/worker lifetime.

## Translate Failures Without Hiding Their Cause

Translate an exception only at a boundary that can present a more useful stable API
outcome. Preserve the original cause when the translation is intentional:

```python
try:
    record = store.read(key)
except StoreUnavailable as exc:
    raise CatalogUnavailable("catalog could not be read") from exc
```

Expected behavior: callers receive `CatalogUnavailable` and Python retains the causal
`StoreUnavailable` chain ([Python 3.15.2 exception chaining](https://docs.python.org/3.15/tutorial/errors.html#exception-chaining)).
The class names are illustrative and do not define a required exception taxonomy. A
broad catch that logs and returns success can change the public contract; sensitive
error details and log mechanics belong to the security and logging modules.

## Pair Acquisition With Cleanup Without Suppressing Failure

Exception handlers match subclasses too; an unmatched exception continues through
surrounding code and callers. User-defined ordinary failures normally derive from
`Exception`, not `BaseException`, so cancellation and interpreter-control exceptions
are not accidentally treated as routine application errors.

Resource cleanup should be established as soon as acquisition succeeds:

```python
from contextlib import contextmanager


@contextmanager
def managed_session(factory):
    session = factory()
    try:
        yield session
    finally:
        session.close()
```

Assumption: `factory` returns a closable resource. Failure in the `with` body still
reaches `close()`. If acquisition itself raises, no session was returned to this
manager; partially acquired state belongs to the acquisition implementation. A
context manager's `__exit__()` is called only after successful `__enter__()`.

Cleanup can change what callers observe. A truthy `__exit__()` return suppresses the
body's exception; a generator context manager that catches merely to log must re-raise
unless suppression is intentional. Likewise, this function hides its own failure:

```python
def hides_failure():
    try:
        raise ValueError("invalid record")
    finally:
        return "success"  # Discards the pending exception; do not use this pattern.
```

Ordinary `finally` cleanup preserves a pending exception, but a return can discard it
and a new cleanup exception changes the propagated failure (retaining context).
`raise ... from None` suppresses display of context, not the stored context itself.
These mechanics deserve failure-path tests; they do not guarantee cleanup after
process termination or a crash. See [compound statements](https://docs.python.org/3.15/reference/compound_stmts.html),
[exception chaining](https://docs.python.org/3.15/library/exceptions.html#exception-context),
and [contextlib](https://docs.python.org/3.15/library/contextlib.html).

## Brownfield Decision

Preserve public signatures, imports, failure outcomes, timeout behavior, and retry
configuration unless the requested change addresses an evidenced compatibility or
reliability problem. If the actual client or endpoint version is unknown, treat its
retry, redirect, deadline, and exception behavior as unresolved rather than borrowing
the urllib3 example. The cited urllib3 details are pinned to 2.6.3; RFC 9110 does not
settle any endpoint's transaction result.

## Related Domains

- Runtime and platform support belong to [Project Context and Layout](project-context-and-layout.md).
- Ruff/Pyright configuration and diagnostic scope belong to [Static Quality](static-quality.md).
- Task cancellation and executor lifecycle belong to [Async and Concurrency](async-and-concurrency.md).
