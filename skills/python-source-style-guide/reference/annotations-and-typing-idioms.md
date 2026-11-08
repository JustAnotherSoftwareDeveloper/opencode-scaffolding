# Annotations And Typing Idioms

## Separate Three Meanings

An annotation can explain intent and support static analysis, but Python does not
automatically validate runtime values against it. The language accepts annotation
expressions broader than the subset that a static typing tool interprets as types; a
framework may also inspect annotations at runtime. Keep three questions distinct:

- What syntax does the target interpreter parse?
- What does the selected type checker understand?
- What does the running program or framework do with annotations?

The Python `typing` documentation states that the runtime does not enforce annotations.
The Typing specification defines type-checker semantics; it does not constrain every
annotation expression the parser accepts ([Python 3.15.2 typing documentation](https://docs.python.org/3.15/library/typing.html); [Typing specification: Annotations](https://typing.python.org/en/latest/spec/annotations.html)).

For new or unconfigured code, this guide proposes annotating public functions and
nontrivial internal functions where types clarify their inputs and results. That is a
contextual source-style choice, not a checker selection or universal coverage rule.
Do not backfill an established project solely to satisfy it. Checker configuration belongs to
`python-project-reference -> reference/static-quality.md`; advertised typed API promises
belong to `python-project-reference -> reference/source-and-api.md`.

Whether a library advertises a complete typed interface, ships stubs, or includes a
typing marker is a separate public-interface and distribution decision, not a rule about
how to spell one annotation. Do not infer those promises from the examples here; load
`python-project-reference -> reference/distribution-artifacts.md` when shipped type
information is the question.

## Choose Types That Match The Contract

Use an abstract input type when callers may supply several compatible implementations,
and a concrete return when the function promises one. For example, `Sequence[str]`
allows ordered indexable inputs, while the returned value below is either one string or
`None`:

```python
from collections.abc import Sequence


def first_label(labels: Sequence[str]) -> str | None:
    if not labels:
        return None
    return labels[0]
```

This combined syntax requires Python 3.10 or newer: `collections.abc` generics are
available from Python 3.9, while `X | Y` union syntax is available from Python 3.10.
Use older compatible spellings if the project's declared support range requires them
([PEP 585](https://peps.python.org/pep-0585/); [PEP 604](https://peps.python.org/pep-0604/)).

Use `object` when a function truly accepts any Python value but the caller should still
be required to narrow the type before using type-specific operations. Reserve `Any`
for a deliberate boundary where static checking should be relaxed:

```python
from typing import Any


def inspect_unknown(value: object) -> str:
    if isinstance(value, str):
        return value.strip()
    return type(value).__name__


def cross_dynamic_boundary(value: Any) -> Any:
    return value.run()
```

The `object` example must narrow before string operations; `Any` permits operations
without that checking and can hide mistakes. An annotation still does not validate the
runtime input. Typing best practices are explicitly evolving and contextual, not a
mandatory project standard ([Typing Best Practices: `Any` And `object`](https://typing.python.org/en/latest/reference/best_practices.html#any-and-object)).

Use a `Protocol` when a named structural capability is useful to callers, not merely
to avoid naming a concrete type:

```python
from typing import Protocol


class HasLabel(Protocol):
    label: str


def label_for(value: HasLabel) -> str:
    return value.label
```

`typing.Protocol` was added to the standard library in Python 3.8. The example is
useful when unrelated objects satisfy the same small capability; it adds needless
indirection if one concrete class is the stable contract
([Python 3.15.2 `typing.Protocol`](https://docs.python.org/3.15/library/typing.html#typing.Protocol)).

## Treat Alias Syntax As A Versioned Choice

```python
InvoiceId = str
```

This assignment binds a runtime name to `str`; it does not make an `InvoiceId` value
nominally distinct from a string. The `type InvoiceId = str` statement was added in
Python 3.12. A `NewType` or a dedicated class may express a stronger distinction, but
that is a type/API design decision rather than formatting. Do not use newer syntax
outside the declared support range ([Python 3.15.2 type aliases](https://docs.python.org/3.15/library/typing.html#type-aliases)).

Annotating `__init__` with `-> None` makes its return intent explicit and follows the
Typing specification's guidance for methods. Whether every initializer must spell it
out is the project's annotation convention, not a universal quality gate
([Typing specification: Annotations](https://typing.python.org/en/latest/spec/annotations.html)).

## Understand Future Imports And Runtime Evaluation

Annotation evaluation has changed across Python versions, so a forward-reference style
can affect runtime consumers as well as checkers. Before Python 3.14, annotation
expressions were ordinarily evaluated when the function or class definition ran.
`from __future__ import annotations` instead stores stringized annotations in the
versions covered by the inspected documentation. Beginning with Python 3.14, the
default model is deferred evaluation; the future import continues to select stringized
behavior in the inspected Python 3.14/3.15 documentation. These are distinct runtime
models, not alternative spellings for runtime validation ([Python 3.14 release notes](https://docs.python.org/3.15/whatsnew/3.14.html); [Typing specification: `__future__` annotations](https://typing.python.org/en/latest/spec/annotations.html)).

For example, this forward reference can be written directly with the future import on
versions where that import is part of the module contract:

```python
from __future__ import annotations


class Node:
    def next_node(self) -> Node | None:
        return None
```

The `|` union form is supported from Python 3.10; the future import changes annotation
evaluation, not the project's interpreter or checker compatibility promise.

Do not add the future import automatically to a brownfield module. Frameworks,
decorators, serializers, and introspection code can depend on whether annotations are
values, strings, or deferred expressions. Test such consumers on the supported
interpreters before changing that behavior.

The timing difference is observable with a deliberately effectful annotation:

```python
events = []


def label_type():
    events.append("annotation evaluated")
    return str


def read_label(label: label_type()) -> str:
    return label
```

Without the future import, Python before 3.14 calls `label_type()` while defining
`read_label`; under the 3.14+ default, that call is deferred until evaluation is needed,
such as reading `read_label.__annotations__`. With the future import, annotations are
stored as strings instead; resolving those strings can still execute the call. This
example demonstrates runtime timing, not recommended static type-hint syntax: the
language accepting an expression does not make it a valid type expression. Prefer
ordinary type names in annotations, and do not rely on annotation side effects for
program initialization.

Python 3.14 introduced `annotationlib` for annotation introspection. Its current
documentation warns that most introspection functionality can execute arbitrary code;
do not treat annotation inspection as harmless parsing of untrusted data
([Python 3.15.2 `annotationlib`](https://docs.python.org/3.15/library/annotationlib.html)).
Requesting string or forward-reference output is not a general sandbox: these formats
do not guarantee that annotation inspection executes no code. Use introspection only
with the same trust assumptions as the code that supplies the annotations.

## Brownfield Safeguards And Boundaries

- Check the declared Python support range before adding built-in generics (3.9+), union
  syntax (3.10+), or the `type` alias statement (3.12+). Also check actual checker and
  framework support; syntax compatibility alone is not enough.
- Preserve established annotation coverage and runtime introspection behavior unless
  the requested outcome explicitly changes them. Do not infer that string annotations
  are runtime-enforced or harmless to evaluate.
- Keep public typed-interface promises with
  `python-project-reference -> reference/source-and-api.md`, and checker selection,
  configuration, and result interpretation with
  `python-project-reference -> reference/static-quality.md`.

## Evidence Scope

The versioned Python 3.15.2 docs and named PEP feature versions support the syntax and
runtime distinctions described here. Typing project's `/latest/` specification and
best-practices pages are mutable and did not surface a numbered release when inspected
on 2026-11-07. PEPs 585/604 identify historical feature-introduction boundaries; use
current Python documentation for present semantics.
These sources do not choose a project's minimum Python version, checker, annotation
coverage, or public typed-interface promise. Verify those against the target project
before applying a version-sensitive example.
