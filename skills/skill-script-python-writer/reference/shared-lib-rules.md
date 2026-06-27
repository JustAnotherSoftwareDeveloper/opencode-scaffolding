# Shared Library Rules

Shared utility modules live in `src/lib/shared/` and are imported by multiple scripts.
This follows the "Scripts plus lib" pattern where cross-script utilities are organized by domain rather than by consumer script.

## Five Shared Module Rules

Every shared module must follow these conventions:

1. **No CLI entry points** — Shared modules are library code only.
   They are imported, never invoked via `uv run`.
   No entry point registration in `[project.scripts]`.

2. **100% test coverage** — Shared modules must meet the same `fail_under = 100` coverage target as per-script packages.
   Tests live in `tests/test_shared_<module>.py`.

3. **Consumer documentation** — Each shared module must declare its consumer scripts in a module-level docstring:

   ```python
   """File/path utilities shared by: collect-skills, count-tokens, validate-skill."""
   ```

4. **Domain-based naming** — Module names describe the utility domain (`files.py`, `schema.py`, `git.py`), not the consuming script.
   This prevents rename churn when new scripts import the same module.

5. **Extraction rule** — Keep utility code in a per-script lib package until a second script needs it.
   Extract to `src/lib/shared/` only when the function or class is imported by two or more scripts.
   Premature extraction is discouraged — a single consumer does not justify shared placement.

## File Layout

```text
scripts/python/
  src/
    cli/                          # CLI entry points (click)
    lib/
      <script_name>/              # per-script lib packages
        __init__.py
        core.py
      shared/                     # shared utilities (cross-script)
        __init__.py               # empty or re-exports
        files.py                  # file/path utilities (glob, read, write, path resolution)
        schema.py                 # JSON Schema validation utilities
        git.py                    # Git-root walkup utilities
        output.py                 # Stdout/stderr formatting helpers
  tests/
    test_shared_files.py
    test_shared_schema.py
```

Modules are organized by domain (`files.py`, `schema.py`, `git.py`, `output.py`) not by consumer script.
This prevents duplication when multiple scripts need the same utility.

## Import Convention

Shared modules are imported using the dotted path `lib.shared.<module>`:

```python
from lib.shared.files import find_files_by_glob
from lib.shared.schema import validate_json_schema
```

This convention works identically in CLI entry points, per-script lib modules, and tests because the existing `sys.path.insert(0, WORKSPACE_ROOT)` pattern (where `WORKSPACE_ROOT = src/`) resolves `lib.shared.<module>` regardless of which script or test imports it.

**Import from a CLI entry point** (`src/cli/<script_name>.py`):

```python
import click
from lib.shared.files import resolve_path
from lib.<script_name>.core import compute
```

**Import from a per-script lib module** (`src/lib/<script_name>/core.py`):

```python
from lib.shared.schema import validate_json_schema
```
