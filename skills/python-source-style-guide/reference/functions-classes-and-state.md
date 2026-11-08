# Functions, Classes, And State

## Put Each Responsibility At A Useful Boundary

Use descriptive action names for functions and methods, such as `read_invoice`,
`is_expired`, or `serialize_report`. Use a class when it groups meaningful state and
behavior, represents a value or concept, or gives instances a useful lifecycle. Use a
function or module-level function when object state and abstraction add no clarity.
There is no source-supported universal function-size, argument-count, or rule requiring
one class per file. Choose boundaries by cohesion, call-site clarity, lifecycle, and the
project's interface rather than an arbitrary threshold ([PEP 8: Naming and class guidance](https://peps.python.org/pep-0008/#naming-conventions)).

Use keyword arguments when names make similar values clearer; positional arguments
remain suitable for short, conventional calls. A helper earns its place when its name,
reuse, isolation, or contract clarifies the work. Avoid both one oversized routine with
unrelated concerns and a wrapper that only renames a direct call.

```python
def normalize_email(value: str) -> str:
    normalized = value.strip().casefold()
    if not normalized:
        raise ValueError("email address must not be empty")
    return normalized
```

The input, transformation, and invalid case are visible. This normalization is only an
example; email identity rules belong to the application's contract.

## Make Parameter Roles Easy To Recognize

Use `self` for an instance method's first parameter and `cls` for a class method's
first parameter. These are PEP 8 conventions, not reserved words. Their consistent use
lets a reader distinguish instance state from construction through the class:

```python
class Amount:
    def __init__(self, cents: int = 0) -> None:
        self.cents = cents

    @classmethod
    def from_cents(cls, cents: int) -> "Amount":
        return cls(cents=cents)
```

Keep parameter/default spacing consistent: `def scale(value, factor=1):` has no
spaces around an unannotated default's `=`, while `factor: int = 1` uses spaces around
`=` with an annotation. A keyword call remains `scale(value, factor=2)`. These forms
help readers separate parameter names, type intent, and defaults; they do not authorize
changing an existing callable's signature
([PEP 8: Function And Method Arguments](https://peps.python.org/pep-0008/#function-and-method-arguments);
[Other Recommendations](https://peps.python.org/pep-0008/#other-recommendations)).

## Decompose Without Moving The Contract

An all-in-one export function hides several responsibilities:

```python
def export_customer(customer, destination):
    validate_customer(customer)
    query = make_sql(customer)
    write_audit_log(customer)
    payload = serialize_customer(query)
    write_payload(destination, payload)
    send_completion_email(customer)
```

One behavior-preserving decomposition can isolate the serialization-and-write unit:

```python
def _write_export(query, destination):
    payload = serialize_customer(query)
    write_payload(destination, payload)


def export_customer(customer, destination):
    validate_customer(customer)
    query = make_sql(customer)
    write_audit_log(customer)
    _write_export(query, destination)
    send_completion_email(customer)
```

The orchestrator still shows the observable order: validate, build the query, audit,
serialize/write, then notify. The helper is useful if that unit has an independent
meaning or test boundary. Moving serialization before the audit, notifying before the
write, swallowing an error, or changing cleanup can change the contract. Do not split
blindly when ordering, transaction scope, or failure behavior is itself the operation's
purpose. Public failure and retry promises belong to
`python-project-reference -> reference/source-and-api.md`.

Avoid a wrapper with no adaptation or contract:

```python
def get_customer(customer_id):
    return _get_customer(customer_id)


def _get_customer(customer_id):
    return repository.get(customer_id)
```

The extra hop does not explain validation, translation, isolation, or a stable boundary.
Keep it only if the public/private split or adapter has a real purpose.

## Prevent Shared Mutable Defaults

Python evaluates a parameter's default expression once when the `def` statement runs,
not once per call. A mutable default therefore persists between calls that omit the
argument ([Python 3.15.2 function definitions](https://docs.python.org/3.15/reference/compound_stmts.html); [Google Python Style Guide: Default Argument Values](https://google.github.io/styleguide/pyguide.html#s2.12-default-argument-values)).

```python
def append_event(event, events=[]):
    events.append(event)
    return events


first = append_event("created")
second = append_event("sent")
```

`first` and `second` refer to the same list; after the second call both contain
`["created", "sent"]`. That is surprising if each call was meant to start fresh.

Use a per-call initialization when omission means “make a new list”:

```python
def append_event(event, events=None):
    if events is None:
        events = []
    events.append(event)
    return events
```

Now calls that omit `events` get independent lists, while an explicitly supplied list
is still mutated. This `None` sentinel is appropriate only when `None` itself does not
mean a separate input value. If it does, use a private unique sentinel or a different
API shape; do not silently collapse two meanings.

## Make State Ownership Explicit

A mutable class attribute is shared by instances that read and mutate that object:

```python
class RequestCounter:
    counts = {}

    def record(self, customer_id):
        self.counts[customer_id] = self.counts.get(customer_id, 0) + 1
```

Two `RequestCounter` objects update the same dictionary. Attribute lookup finds the
class attribute until an instance shadows the name; mutating the dictionary through
`self.counts[...]` changes the shared object rather than creating an instance value.
This is useful only if shared ownership is intentional and its lifecycle is clear.

For per-instance counts, initialize a new mapping on each object:

```python
class RequestCounter:
    def __init__(self):
        self.counts = {}

    def record(self, customer_id):
        self.counts[customer_id] = self.counts.get(customer_id, 0) + 1
```

Use class attributes for genuinely class-wide data such as immutable constants, or for
mutable shared registries only when shared behavior is deliberate. If a value should
belong to one object, initialize it in `__init__`; a class and instance attribute are
not interchangeable spellings for that state ([Python 3.15.2 class definitions](https://docs.python.org/3.15/reference/compound_stmts.html)).

## Keep Objects When State And Behavior Belong Together

This stateful object owns both its schedule and position:

```python
from collections.abc import Sequence


class RetrySchedule:
    def __init__(self, delays: Sequence[float]) -> None:
        self._delays = tuple(delays)
        self._next_index = 0

    def next_delay(self) -> float | None:
        if self._next_index >= len(self._delays):
            return None

        delay = self._delays[self._next_index]
        self._next_index += 1
        return delay
```

Each instance can advance independently. The `collections.abc` generic form requires
Python 3.9 or newer, and `float | None` requires Python 3.10 or newer; therefore this
combined example needs Python 3.10+. The example says nothing about safe retry policy,
delay bounds, or whether a real operation can be replayed
([PEP 585](https://peps.python.org/pep-0585/); [PEP 604](https://peps.python.org/pep-0604/)).

By contrast, a class that only namespaces one unrelated function may add indirection:

```python
class TextHelpers:
    @staticmethod
    def slugify(value: str) -> str:
        return value.strip().lower().replace(" ", "-")
```

If the operation has no instance state, polymorphic contract, or cohesive grouping
purpose, a module-level function is simpler. A utility-class pattern may still be an
established project convention; do not rewrite a public object model just to apply this
proposal. Google explicitly allows related classes and top-level functions to share a
module; that is an exemplar, not a universal repository layout rule
([Google Python Style Guide: Packages](https://google.github.io/styleguide/pyguide.html#s2.3-packages)).

## Existing-Project Safeguards And Boundaries

- Preserve established call signatures, public names, instance lifecycle, state
  sharing, and ordering of side effects unless the requested outcome authorizes a
  bounded change.
- Check whether a default object or class attribute is intentionally shared before
  changing it. A “cleanup” can alter callers' observed state.
- Keep module/file placement with
  `python-project-reference -> reference/project-context-and-layout.md`; keep task,
  thread, and cancellation ownership with
  `python-project-reference -> reference/async-and-concurrency.md`.
- Do not turn a useful boundary judgment into a maximum number of lines, parameters,
  helpers, or classes per module.

## Evidence Scope

The Python 3.15.2 language reference supports default-expression evaluation and
class/instance attribute semantics. PEP 8 supports naming and visibility conventions;
Google's function-length and module-sharing guidance is its house style. Sources were
inspected on 2026-11-07; the live Google guide exposed no numbered revision. The
evidence supplies behavior and examples, not an ideal function size, universally useful
class boundary, or comparative maintainability result.
