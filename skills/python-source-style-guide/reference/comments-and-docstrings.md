# Comments And Docstrings

## Put The Explanation Where It Helps

Use a comment to explain a non-obvious path, a constraint not apparent from the code,
or a trade-off that a future maintainer might otherwise undo. Keep it accurate as the
implementation changes. If the code is hard to follow, first consider whether a clearer
name or control flow would remove the need for narration.

```python
# Keep the original offset: the downstream API interprets it in the source file.
offset = parsed_record.source_offset
```

The comment records why this value must not be recomputed. By contrast, this only
repeats the operation:

```python
# Add one to count.
count += 1
```

An outdated or contradictory comment is worse than no comment because it can lead a
reader to trust a false explanation. PEP 8 makes accuracy a direct recommendation
([PEP 8: Comments](https://peps.python.org/pep-0008/#comments); dossier C07).

## Write Docstrings For Caller-Relevant Behavior

PEP 257 defines an ordinary docstring as the first string-literal statement in a module,
function, class, or method. That string becomes the object's `__doc__`. PEP 257
recommends a concise summary and, when useful, a blank line followed by detail; it does
not prescribe a markup system ([PEP 257: What Is A Docstring?](https://peps.python.org/pep-0257/#what-is-a-docstring); [Multi-line Docstrings](https://peps.python.org/pep-0257/#multi-line-docstrings); dossier C07).

A useful docstring says what callers need beyond what the signature already expresses:

```python
def read_invoice(invoice_id: str) -> Invoice:
    """Return the invoice identified by `invoice_id`.

    The returned invoice reflects the latest committed version.

    Args:
        invoice_id: Stable identifier assigned by the billing system.

    Returns:
        The matching invoice.

    Raises:
        InvoiceNotFound: No invoice exists for `invoice_id`.
        BillingUnavailable: The billing store cannot be reached.
    """
    ...
```

The freshness promise and failure cases are not encoded by the annotations. For a real
API they must match implemented behavior and supported contract; this illustrative
example makes no promise about an existing billing system. A docstring can be concise
when the signature and context already answer the reader's question.

Avoid repeating a signature without adding behavior:

```python
def read_invoice(invoice_id: str) -> Invoice:
    """Read invoice_id: str and return Invoice."""
```

The reader learns no identifier meaning, consistency guarantee, side effect, or failure
condition. Do not fill `Args`, `Returns`, or `Raises` sections just because a format
offers them; include the information that changes how a caller uses the function.

## Choose A Markup Format With Its Audience And Toolchain

For a new general-purpose project that has no established documentation format, this
guide proposes a concise summary and Google-style `Args`, `Returns`/`Yields`, and
`Raises` sections when they add useful detail. Google's format is a practical exemplar,
not a PEP requirement. NumPy's contributor and API-documentation workflow recommends
numpydoc with Sphinx and uses section headings such as `Parameters`, `Returns`,
`Raises`, and `Examples`. PEP 257 deliberately leaves markup open, so retain the
established format rather than converting a project just to match either example
([Google Python Style Guide: Comments And Docstrings](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings); [NumPy documentation guide](https://numpy.org/doc/stable/dev/howto-docs.html); [numpydoc style guide](https://numpydoc.readthedocs.io/en/stable/format.html); dossier C07).

The same hypothetical contract can be presented in a NumPy-style form:

```python
def read_invoice(invoice_id):
    """Return the invoice identified by ``invoice_id``.

    Parameters
    ----------
    invoice_id : str
        Stable identifier assigned by the billing system.

    Returns
    -------
    Invoice
        The latest committed invoice.

    Raises
    ------
    InvoiceNotFound
        If the identifier has no record.
    """
    ...
```

This demonstrates a formatting choice, not parity with every detail of the Google
example. Choose a format based on existing reader expectations, documentation
generation, and project convention. In a NumPy/Sphinx ecosystem, numpydoc sections may
be the most useful fit; elsewhere, a different established format can be better. The
NumPy `mean` reference illustrates parameter constraints, return details, notes, and
examples, but one reference page does not prove that every project needs that level of
detail ([NumPy `mean` reference](https://numpy.org/doc/stable/reference/generated/numpy.mean.html); dossier C07).

## Know What Is And Is Not Available At Runtime

An object's ordinary docstring is available through `__doc__`. PEP 257 also names
attribute and additional docstrings as string literals that documentation tools may
extract; they are not the same as the object's first-statement docstring and are not
exposed as ordinary runtime `__doc__` metadata by the compiler.

```python
class Invoice:
    """A billable record."""

    total = 0
    """Net amount before tax; documentation tools may extract this text."""
```

`Invoice.__doc__` is the class docstring. Do not assume the second string becomes
`Invoice.total.__doc__`; rely on it as documentation only when the project's chosen
tooling recognizes attribute docstrings ([PEP 257: Specification](https://peps.python.org/pep-0257/#specification); dossier C07).

For a class, explain what the abstraction represents and any important usage or
lifecycle constraint. For a module, explain its non-obvious purpose or supported entry
points. Neither needs a prose copy of every attribute and function; document the parts a
reader cannot infer safely from the names and signatures.

## Brownfield Safeguards And Boundaries

- Preserve a project's existing Google, NumPy/numpydoc, reStructuredText, or other
  documented format. A docstring-style change can affect rendered output and tooling.
- Verify any documented return, failure, freshness, side-effect, or lifecycle promise
  against the actual public contract. Docstrings do not create behavior or API policy.
- Public API commitments belong to `python-project-reference -> reference/source-and-api.md`;
  packaged documentation and artifact contents belong to
  `python-project-reference -> reference/distribution-artifacts.md`.

## Evidence Scope

PEP 257 supports docstring meaning, summary/detail structure, and the runtime distinction
for additional strings. Google and NumPy/numpydoc document their own formats; the
inspected NumPy sources identify the v2.5 Manual, while the numpydoc `stable` page did
not surface a numbered release. The fixed dossier was retrieved on 2026-11-07; see C07
and source register S02, S14, and S16-S18. These sources do not mandate a markup format
for an unrelated project or prove that one format improves outcomes universally.
