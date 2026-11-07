# Project Context And Layout

## Start With Delivery And Support

Before choosing a tree, distinguish an application intentionally run from a checkout
from a package installed by consumers. “Python project” does not imply that it needs a
wheel, a reusable public API, or a layered service architecture.

Keep three support facts separate:

- **Declared:** metadata such as `[project].requires-python` expresses a Python-version
  requirement.
- **Selected:** an interpreter file or local environment chooses what one invocation
  uses.
- **Tested:** a test or build result establishes only the target it actually exercised.

`requires-python` is not evidence that every declared Python and platform combination
was tested. Python-version metadata also does not describe an operating system, Python
implementation, runtime image, or system-library promise. (Dossier C02; see the [PyPA
`pyproject.toml` specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/).)

## Choose A Layout For Its Import Boundary

For a new distributable library, `src/<package>/` with tests outside `src/` is a
useful starting point when you want development and tests to exercise an installed
package path. PyPA documents the trade-off: source code is not importable merely
because the checkout is the current directory, so the developer must install the
package (often editably). That can expose missing installation/package configuration
that a checkout import hides. It adds an installation step; it does not prove a
universal maintainability advantage. (C01, C32; [PyPA layout discussion](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/).)

```text
pyproject.toml
src/
  acme_metrics/
    __init__.py
    api.py
tests/
  test_api.py
```

Assumption: `acme_metrics` is intended to be installed as a distribution. A smoke test
that succeeds only when run inside the checkout may have imported the repository copy,
not the installed artifact. Python 3.15.2 places the script directory—or the current
directory for interactive, `-c`, and `-m` execution—first on `sys.path`; inspect the
actual winner instead of inferring it from the test result:

```sh
python -c 'import acme_metrics; print(acme_metrics.__file__)'
```

The observable value is the imported module's path. Compare it in the checkout and in
the consumer-like environment; no path is asserted here because none was run. (C32;
[Python 3.15.2 path initialization](https://docs.python.org/3.15/library/sys_path_init.html).)

A small application deliberately launched from its repository may keep a flat layout
if its existing import and deployment model is intentional. A service's modules should
follow its real entry points, framework, and cohesive responsibilities; Django or
FastAPI tutorial trees are examples for those frameworks, not interchangeable generic
service templates.

## Diagnose Before Moving A Brownfield Project

If an installed import fails while checkout tests pass, compare `module.__file__`, the
invocation directory, the installed distribution, and its built contents. A checkout
path winning import resolution points toward an import-path or packaging test gap; it
does not by itself prove that moving to `src/` is the only fix.

For an established project, retain working import paths, package form, framework
organization, test placement, and support declarations unless a requested outcome or
approved policy calls for a bounded change. A move to `src/`, package rename, namespace
conversion, or directory-layer split can change imports and consumers. Make those
effects visible before proposing a migration. The evidence supports import/layout
trade-offs, not a universal application tree or a target project's tested support
matrix. (C01-C02, C32.)

## Related Domains

- Public imports, API promises, and typed-client compatibility belong to [Source and API](source-and-api.md).
- Test design and coverage scope belong to [Testing and Coverage](testing-and-coverage.md).
- Distribution metadata and artifact contents belong to [Distribution Artifacts](distribution-artifacts.md).
- General naming, import, docstring, and annotation style belongs to `python-source-style-guide -> reference/python-source-style-guide.md` when that guide is explicitly loaded.
