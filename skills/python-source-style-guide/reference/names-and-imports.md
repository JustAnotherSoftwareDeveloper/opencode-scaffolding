# Names And Imports

## Choose Names That Reveal Roles

For new or unconfigured code, this guide proposes recognizable role-based forms:
`snake_case` for functions, methods, variables, and ordinary module/package names;
`CapWords` for classes and exceptions; and `UPPER_SNAKE_CASE` for module-level
constants. Prefer a name that tells the reader what a value represents, including its
unit when that matters.

```python
DEFAULT_TIMEOUT_SECONDS = 5.0


class InvoiceNotFound(Exception):
    pass


def load_invoice(invoice_id: str) -> Invoice:
    ...
```

`load_invoice` identifies an action and `invoice_id` gives more context than `id`.
These spellings are conventions, not syntax requirements. PEP 8 gives role-based
recommendations for its stated scope ([PEP 8: Naming Conventions](https://peps.python.org/pep-0008/#naming-conventions)).

```python
T = 5.0


class invoice_not_found(Exception):
    pass


def get(x):
    ...
```

Those names hide role or depart from the conventional casing. A short local such as
`i` can still be clear in a small index loop; do not replace meaningful names merely to
avoid every one-character identifier.

Use one leading underscore to signal that a name is for internal use. It does not
enforce access control. Double-leading underscores in a class body trigger name
mangling and are useful only when avoiding subclass attribute collisions is an actual
need; they are not stronger privacy. Public names should be chosen deliberately, but
do not rename an established import or symbol as a style-only cleanup. For example, a
consumer that imports `Invoice` will fail if a package removes that name:

```python
from acme.billing import Invoice
```

A compatibility alias or deprecation may help, but the API owner decides whether and
how to provide one. A documented public name is part of what callers may import, so a
rename can break their code
([PEP 8: Public and Internal Interfaces](https://peps.python.org/pep-0008/#public-and-internal-interfaces); `python-project-reference -> reference/source-and-api.md`).

Python accepts valid non-ASCII identifiers and normalizes identifier text using NFKC;
an ASCII preference is therefore a coordination choice, not a parser rule. PEP 8's
ASCII policy is scoped to the standard library. Preserve an established domain or
language choice rather than treating ASCII as a security or universal style mandate
([Python 3.15.2 lexical analysis](https://docs.python.org/3.15/reference/lexical_analysis.html#identifiers); [PEP 3131](https://peps.python.org/pep-3131/)).

## Group Imports So Their Origins Are Visible

PEP 8 recommends imports near the top of the module, grouped as standard library,
third-party, then local application/library code, with blank lines between groups. It
recommends absolute imports but permits explicit relative imports when they make a
complex package layout clearer. For a new or unconfigured module, this guide proposes
explicit imports and readable absolute paths as a starting point; Google's stricter
no-relative-import choice is a Google house rule, not a universal Python requirement
([PEP 8: Imports](https://peps.python.org/pep-0008/#imports); [Google Python Style Guide: Packages](https://google.github.io/styleguide/pyguide.html#s2.3-packages)).

```python
import json
from pathlib import Path

import httpx

from acme.billing.models import Invoice
from acme.billing.store import InvoiceStore
```

Keep imports explicit when doing so makes dependencies and names easier to locate.
`import numpy as np` is a familiar alias; `element_tree` explains more than an opaque
`et`. Importing a module can make ownership visible at the call site, while selecting
names can keep a simple call concise. Prefer the spelling that fits the package and
existing local practice; the evidence does not establish a universal module-versus-name
rule. For example, compare a module-qualified call with an imported name:

```python
from acme.billing import store

invoice = store.load_invoice(invoice_id)
```

```python
from acme.billing.store import load_invoice

invoice = load_invoice(invoice_id)
```

The first keeps the owner visible at each call; the second removes a repeated qualifier
when the imported name already explains its role. Google's module/package-import rule
also has typing-related exemptions, so do not read it as banning every direct import
of a type ([Google Python Style Guide: Imports](https://google.github.io/styleguide/pyguide.html#s2.2-imports);
[Imports For Typing](https://google.github.io/styleguide/pyguide.html#s3.19.12-imports-for-typing)).

NumPy contributor code uses `import numpy as np`, while NumPy documentation examples
need not repeat that import at the start. An example written for that prepared
documentation context is not necessarily a self-contained script. Include required
imports when presenting a standalone example; do not generalize the documentation
exception to application modules ([NumPy contributor guide](https://numpy.org/doc/stable/dev/index.html);
[NumPy documentation guide](https://numpy.org/doc/stable/dev/howto-docs.html)).

Avoid wildcard imports and compressed mixed forms in ordinary modules:

```python
from acme.billing.models import *
import json, pathlib
```

Wildcards make the local namespace and source of names harder to inspect. A deliberate
public re-export is a different case: import the supported names explicitly and expose
the intended API, for example with `__all__`. PEP 8 recognizes republishing an internal
interface as a defensible wildcard use, but a documented explicit export is easier to
review and maintain. Import sorting and enforcement belong to
`python-project-reference -> reference/static-quality.md`.

For package-local imports, compare these alternatives in the context of the real
package:

```python
from acme.billing.models import Invoice
```

```python
from .models import Invoice
```

The absolute form names the package from its root and is easy to search outside the
current directory. The relative form makes the neighboring-package relationship
visible and can avoid a long repeated prefix. Relative imports require package context;
entry points and established test/import practice can matter. Do not convert imports
mechanically or claim that either spelling alone resolves a cycle. Preserve the form
the project actually supports unless a scoped change addresses a concrete issue.

## Place Module-Level Dunders Before Ordinary Imports

PEP 8 has a separate ordering rule for module-level dunder names such as `__all__`,
`__author__`, and `__version__`: place them after the module docstring but before
imports, except `from __future__` imports. The language requires future imports before
other code apart from the module docstring. Then place ordinary imports in their
groups; ordinary module initialization follows them
([PEP 8: Module Level Dunder Names](https://peps.python.org/pep-0008/#module-level-dunder-names); [Python compound statements](https://docs.python.org/3.15/reference/compound_stmts.html); the PEP 8 ordering passage was checked on 2026-11-07).

```python
"""Billing models exposed by this package."""

from __future__ import annotations

__all__ = ["Invoice"]
__version__ = "1.0"

import json
from pathlib import Path

from acme.billing.models import Invoice

DEFAULT_TIMEOUT_SECONDS = 5.0
```

This example shows placement, not a requirement to define `__all__` or `__version__`.
The key exception is that the future import comes before the module dunders; those
dunders precede ordinary imports. Keep project-specific metadata conventions intact.

## Existing-Code Safeguards

- Preserve established public spellings, imports, aliases, and export lists. Check the
  caller-visible API before treating a rename or import-path change as cleanup.
- Follow a project's existing absolute/relative import choice unless the requested
  change has a reason to alter it.
- Keep local imports narrow and explain the specific constraint they address; do not
  use them as the default way to organize dependencies.
- Do not infer formatter or import-sorter rules from these examples. Use the project's
  configured tools and `python-project-reference -> reference/static-quality.md`.

## Evidence Scope

PEP 8 is the primary convention source and explicitly scopes itself to the standard
library. The direct Python 3.15.2 lexical reference supports identifier mechanics, not
the ASCII preference. The Google and NumPy sources describe publisher-specific choices;
their live pages were inspected on 2026-11-07, with NumPy identifying the v2.5 Manual
and Google exposing no numbered revision. These are documentation snapshots, not
universal policy. Check the target project's conventions and support context before
applying a new spelling or import form.
