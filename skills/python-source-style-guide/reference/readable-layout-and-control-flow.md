# Readable Layout And Control Flow

## Format For Scanning, Not For A Line-Count Target

Python's parser and style conventions answer different questions. Indentation defines
syntax; line width, whitespace, and one-statement-per-line guidance are conventions.
PEP 8 recommends four spaces, 79 code columns and 72 comment/docstring columns, while
allowing a team-agreed code width up to 99. Google chooses 80 columns with exceptions.
Those are publisher choices, not parser limits or measured optima. For new or
unconfigured code, this guide proposes four spaces, a 79-column code target, and a
72-column comment/docstring target as starting values. Retain the project's formatter
choice in existing code
([PEP 8: Code Layout](https://peps.python.org/pep-0008/#code-lay-out); [Google Python Style Guide: Line Length](https://google.github.io/styleguide/pyguide.html#s3.2-line-length)).

Use spaces rather than tabs for new indentation. PEP 8 permits tabs to match a file that
already uses them; inconsistent tab/space indentation can fail when Python cannot
resolve the indentation level. Separate top-level functions and classes with blank
lines, and use blank lines inside a function only to mark logical sections. These are
conventions layered over Python's indentation syntax, not a reason to reformat an
unrelated file.

PEP 8 makes no universal choice between single and double quotes for ordinary strings.
This guide proposes double quotes for new, unconfigured code; use single quotes when
they avoid escapes or when the project already uses them. Triple-double quotes are the
published docstring convention. The parser treats ordinary single- and double-quoted
strings equivalently ([PEP 8: String Quotes](https://peps.python.org/pep-0008/#string-quotes)).

Use parentheses, brackets, and braces for implicit continuation where practical. It
keeps a call's structure visible without a backslash:

```python
invoice = build_invoice(
    customer=customer,
    line_items=line_items,
    tax_rate=tax_rate,
)
```

Named arguments help when they clarify similar values. Break long arithmetic where the
operator remains easy to match with its operands; PEP 8 suggests breaks before operators
for new code and explicitly permits a locally consistent alternative. Do not churn a
file to switch an established wrapping style. A short comprehension is useful when its
mapping or filtering purpose is immediately visible; use a loop when conditions,
side-effects, or intermediate decisions make the expression hard to follow.

Prefer one statement per line in new code. Same-line compound statements and
semicolon-separated statements are legal in Python, but PEP 8 discourages them because
the visual structure can obscure sequencing and branches. A formatter may enforce a
subset, but its configuration is not defined here (`python-project-reference -> reference/static-quality.md`).
Python's [lexical rules](https://docs.python.org/3.15/reference/lexical_analysis.html),
[simple statements](https://docs.python.org/3.15/reference/simple_stmts.html), and
[compound statements](https://docs.python.org/3.15/reference/compound_stmts.html)
explain why implicit continuation and same-line statements parse; they do not recommend
one presentation for every reader.

## Expand Dense Code Without Changing Its Branches

Consider a compact version of an invoice workflow:

```python
invoice = build_invoice(customer, line_items, tax_rate) \
    if customer.is_active else None

if invoice: send(invoice); record_sent(invoice)
```

An easier-to-scan expansion preserves two separate decisions:

```python
if customer.is_active:
    invoice = build_invoice(customer, line_items, tax_rate)
else:
    invoice = None

if invoice:
    send(invoice)
    record_sent(invoice)
```

The first condition decides whether to build. The second decides whether to send and
record. If an active customer's builder can return a false-valued invoice, those effects
still do not run. Moving them under only the active-customer branch changes behavior.
The expansion is safe only if it preserves the order, condition, values, and side effects
of the original code. A formatting-only patch should not silently repair or redesign
behavior.

## Use Truth Tests Only When False Means The Same Thing As Missing

Python truth testing can distinguish neither `None` from an empty string nor an empty
container from another false value. `or` returns one of its operands, not a normalized
`bool`; use it only when every false-valued case should take the fallback
([Python 3.15.2 truth-value testing](https://docs.python.org/3.15/library/stdtypes.html#truth-value-testing); [Boolean operations](https://docs.python.org/3.15/library/stdtypes.html#boolean-operations-and-or-not)).

```python
def display_label(record: Record) -> str:
    if record.label is not None:
        return record.label
    return "(untitled)"
```

For this contract, `None` means “not supplied” while an empty string is a deliberate
value. The shorter alternative changes that distinction:

```python
def display_label(record: Record) -> str:
    return record.label or "(untitled)"
```

The `or` form is correct if empty strings and all other false values also mean “missing.”
State that domain rule rather than inferring it from brevity. PEP 8 recommends
`is None` for the singleton test ([PEP 8: Programming Recommendations](https://peps.python.org/pep-0008/#programming-recommendations)).

`and` and `or` also short-circuit: the second expression runs only when needed, and
the result can retain the operand's type rather than becoming `bool`:

```python
label = cached_label or load_label()
can_send = invoice is not None and invoice.is_ready
```

`load_label()` is skipped for a true-valued cached label, but runs for an empty string.
The second expression does not access `is_ready` when `invoice` is `None`. Expanding
either expression must preserve those evaluation conditions. When the domain question
is specifically numeric zero, `remaining == 0` can communicate it more precisely than
`not remaining`; use truthiness when all relevant false-valued cases mean the same thing.

Truth testing is not guaranteed to work for every object. Google's guide calls out
NumPy arrays, whose implicit truth test can raise when the array has more than one
element. That is a useful NumPy-specific warning, not a rule that every custom object
or sequence behaves alike ([Google Python Style Guide: True/False Evaluations](https://google.github.io/styleguide/pyguide.html#s2.14-truefalse-evaluations)).
Custom objects can define `__bool__()` or, if absent, `__len__()`; inspect that contract
before replacing an identity or explicit comparison with an implicit truth test.

## Name An Intermediate When It Carries Meaning

A named intermediate can make a validation decision easier to inspect and debug:

```python
has_required_fields = all(
    field in payload
    for field in ("id", "amount", "currency")
)

if not has_required_fields:
    raise InvalidInvoice("invoice fields are incomplete")
```

The name tells a reviewer what the expression tests. A named predicate can also help
when the decision is reused:

```python
def can_publish(report: Report) -> bool:
    return report.is_complete and not report.has_blocking_findings


if can_publish(report):
    publish(report)
```

If a one-use condition is already clear, extracting a helper may add a jump without
adding meaning. Prefer the representation that makes the important case, failure path,
or side effect visible. There is no evidence-backed universal line, branch, or expression
limit.

## Brownfield Safeguards And Boundaries

- Preserve the current formatter width, quote choice, and local wrapping style in an
  established project. Do not reformat unrelated files to match a proposed default.
- Review a “readability-only” diff for changed conditions, exception behavior, value
  distinctions, evaluation order, and side effects; a green formatter does not prove
  semantic equivalence.
- Formatting examples do not establish API failure behavior, input validation,
  security, logging, asynchronous task ownership, or tests. Load
  `python-project-reference -> reference/source-and-api.md` or another topic only when
  the concrete question crosses that boundary.

## Evidence Scope

PEP 8 and the Python 3.15.2 lexical, compound-statement, and built-in type references
support the distinction between valid syntax and conventions. Google supplies an
80-column house choice and a NumPy truth-testing caveat. The sources were inspected
on 2026-11-07; Google's live guide exposed no numbered revision. They do not establish
an optimal width or prove that expanded syntax always preserves behavior; check the
actual expression and target project's formatter.
