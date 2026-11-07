# Source And API

## Define The Promise Callers Can Observe

For an API decision, name what a consumer can rely on: supported import path and
symbol, accepted arguments, return behavior, side effects, documented exceptions, and
subclass or override behavior when promised. PEP 387 uses these as compatibility
dimensions for CPython; it is an example, not a third-party project's policy. A version
string accepted by PEP 440 does not define an API lifecycle. (Dossier C03; [PEP 387](https://peps.python.org/pep-0387/).)

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

## Diagnose A Timed-Out Request Before Retrying

A timeout after sending a write does not tell the caller whether the server applied the
effect. RFC 9110 permits automatic retry of a non-idempotent request only when its
semantics are known idempotent or the client can determine the original was not
applied. The endpoint's contract—not the method name or a Python client's default—must
establish replay safety. (C04; [RFC 9110 §9.2.2](https://www.rfc-editor.org/rfc/r9110.html#section-9.2.2).)

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
bytes can extend total elapsed time. No call is made by this example. (C23; [urllib3
2.6.3 retry and timeout reference](https://urllib3.readthedocs.io/en/2.6.3/reference/urllib3.util.html).)

When a write acknowledgement is uncertain, the safer alternatives are to avoid blind
replay, consult the endpoint's idempotency/deduplication contract, or reconcile the
operation's state through a supported read path. Do not invent an idempotency-key
contract or assume an SDK retry setting proves one exists. A request-wide deadline is
also different from a per-call/socket timeout; compose one only when the client APIs
support the intended scope.

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

## Brownfield Decision

Preserve public signatures, imports, failure outcomes, timeout behavior, and retry
configuration unless the requested change addresses an evidenced compatibility or
reliability problem. If the actual client or endpoint version is unknown, treat its
retry, redirect, deadline, and exception behavior as unresolved rather than borrowing
the urllib3 example. The cited urllib3 details are pinned to 2.6.3; RFC 9110 does not
settle any endpoint's transaction result. (C03-C04, C23.)

## Related Domains

- Runtime and platform support belong to [Project Context and Layout](project-context-and-layout.md).
- Ruff/Pyright configuration and diagnostic scope belong to [Static Quality](static-quality.md).
- Task cancellation and executor lifecycle belong to [Async and Concurrency](async-and-concurrency.md).
