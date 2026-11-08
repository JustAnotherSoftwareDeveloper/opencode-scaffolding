# Change Design And Validation

## Design Around The Observable Contract

A small implementation diff can have a large compatibility surface. Before choosing
edits, identify the supported imports and call patterns, accepted arguments, returned
values, side effects, and documented failure outcomes. Include subclassing or typed
client behavior only where the project promises it. PEP 387 describes these dimensions
for CPython; use it as a way to find questions, not as a third-party project's removal
schedule ([PEP 387](https://peps.python.org/pep-0387/)).

Keep declared support separate from the interpreter available locally. Running a test
on one Python/platform combination does not validate the complete supported range.
Likewise, changing an annotation can affect typed clients without changing runtime
acceptance, and changing an exception can break callers even when the successful
return value stays the same. Distribution version syntax does not choose an API
compatibility policy ([PyPA Version Specifiers](https://packaging.python.org/en/latest/specifications/version-specifiers/)).

For each affected boundary, record what must stay stable and what the request actually
changes. Preserve existing configuration and compatibility promises before approved
local policy; use proposed defaults only when a new choice is permitted. For the
shared adoption guidance, explicitly load `python-project-reference` and read
`python-project-reference -> reference/project-baseline-and-adoption.md`.

## Worked Change: A Missing Optional Rules File

Assume an existing function reads a JSON object from an optional rules file. The
authorized change is: a missing file means no rules. Malformed JSON, permission
failures, and other I/O errors must retain their existing failure behavior.

A broad `except Exception: return {}` would hide several different failures and make
misconfigured deployments look like successful empty configuration. Catch only the
newly accepted absence:

```python
import json


def load_rules(path):
    try:
        with path.open(encoding="utf-8") as stream:
            return json.load(stream)
    except FileNotFoundError:
        return {}
```

This illustrative change assumes the existing successful input contract already
requires a JSON object; it does not add validation for arrays or other JSON values.
The context manager closes the file even when decoding fails. Catching the specific
exception preserves unrelated propagation rather than treating every failure as
absence ([Python errors and cleanup](https://docs.python.org/3.15/tutorial/errors.html)).

The design review should distinguish these cases:

- Existing valid rules still return the same data through the same public import.
- A missing file now returns an empty mapping, as requested.
- Malformed JSON still raises the established decoding failure.
- A permission failure remains an error, not an empty configuration.
- Cleanup still occurs after successful decoding and after a decoding failure.

Add or adjust only the directly coupled regression cases using the project's existing
test conventions. Do not migrate its fixture framework, add a dependency, or introduce
a new coverage gate to make this source change appear complete. If the project
requires an explicit opt-in for optional configuration, establish that contract before
implementing unconditional absence handling.

## Keep Failure Translation And Retry Separate

Translate an exception when a boundary can offer callers a useful stable failure
contract. Preserve the cause with `raise DomainError(...) from exc`; do not turn a
failure into success merely to avoid a traceback. Use context managers or `finally`
to release resources independently of whether a failure is translated. Exception
chaining preserves diagnostic causality but does not make sensitive exception content
safe to log ([Python exception chaining](https://docs.python.org/3.15/tutorial/errors.html#exception-chaining)).

A timeout also is not proof that an operation had no effect. For a write sent to a
remote service, failure to receive an acknowledgement leaves the result uncertain.
Do not add a generic retry as an incidental “reliability fix”: establish replay safety,
known non-application, or an actual endpoint deduplication/reconciliation contract first.
RFC 9110's idempotency semantics do not certify a particular endpoint
([RFC 9110 §9.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2)).

When the requested change concerns these boundaries, explicitly load
`python-project-reference` and read
`python-project-reference -> reference/source-and-api.md` for timeout/deadline and
replay distinctions. Use
`python-project-reference -> reference/async-and-concurrency.md` only for task,
cancellation, executor, or shutdown mechanics. Do not copy a client library's timeout
numbers into another project or stack retries over an existing SDK policy.

## Validate Different Promises With Different Evidence

Choose checks from the affected contract rather than running a universal checklist:

- **Behavior:** exercise the requested new outcome and representative unchanged cases.
  Include failure paths that could be accidentally hidden or translated.
- **Compatibility:** exercise public imports, old calling patterns, return/error
  behavior, and selected typed-client expectations where they are promised.
- **Static conformance:** use the configured formatter, lint, and type checks for
  changed paths. A clean static result does not execute the behavior; annotations
  are not runtime validation ([Python typing](https://docs.python.org/3/library/typing.html)).
- **Runtime support:** report the actual interpreter/platform combinations exercised.
  A skipped or unavailable target remains untested.
- **State and cleanup:** use focused failure injection where the project supports it;
  verify observable release behavior instead of assuming a passing happy path covers it.

A passing test supports its collected case and assertion, not every requirement
([pytest test anatomy](https://docs.pytest.org/en/stable/explanation/anatomy.html)).
Coverage can reveal an unexecuted error path but cannot certify that the assertion
would detect the wrong behavior. Keep source set, exclusions, measurement mode, and
test-file inclusion visible when reporting coverage
([coverage.py 7.17.2 source selection](https://coverage.readthedocs.io/en/7.17.2/source.html)).

If a failure was already present, preserve its evidence and separate it from findings
introduced by the change. If the new regression exposes a required dependency,
packaging, standalone quality, or unrelated source change, report that boundary rather
than silently repairing it. Test-only work without a production change belongs to the
test operation; distribution installation checks belong to the distribution operation.

## Read More Only At The Affected Boundary

After explicitly loading `python-project-reference`, use its
`reference/project-context-and-layout.md` for imports/support context,
`reference/testing-and-coverage.md` for test state and coverage interpretation, and
`reference/static-quality.md` for configured diagnostic scope. Cite them using the
explicit form `python-project-reference -> reference/testing-and-coverage.md` when
directing another reader.

For a change handling sensitive configuration or output, read
`python-project-reference -> reference/secure-configuration-and-data-handling.md`;
for record routing or correlation, read
`python-project-reference -> reference/logging-and-observability.md`. These supply
different questions: which values may be exposed versus how records are represented
and routed. General source conventions require a separate explicit load of
`python-source-style-guide -> reference/python-source-style-guide.md`.

The cited Python 3.15 and coverage.py 7.17.2 pages describe those documentation scopes;
mutable PEP/PyPA/pytest pages are historical source context, not target-version evidence.
Use the target's supported versions and established commands for executable details.
