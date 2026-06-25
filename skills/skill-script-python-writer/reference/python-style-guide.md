# Python Style Guide

Every generated script and lib module must conform to the project's lint and type-check rules.
These are enforced by `ruff.toml` and `pyrightconfig.json` at `scripts/python/`.

## Ruff Lint Rules

The project enforces these ruff rule categories:

- **E** (pycodestyle errors): Syntax errors, indentation, line breaks.
- **F** (pyflakes): Unused imports, undefined names, duplicate arguments.
- **I** (isort): Import ordering (stdlib, third-party, local).
- **N** (pep8-naming): snake_case functions/variables, PascalCase classes, UPPER_CASE constants.
- **W** (pycodestyle warnings): Trailing whitespace, blank line conventions.
- **UP** (pyupgrade): Modern Python syntax (py312 target).
- **B** (flake8-bugbear): Logical bugs: mutable defaults, bare `except:`, `del` on locals.
- **SIM** (flake8-simplify): Simplify expressions: `if bool(x)` to `if x`, merge nested `if` blocks.
- **ARG** (flake8-unused-arguments): Unused function arguments (suppress with `_` prefix).

**Target version:** `py312` — use 3.12 features (type parameter syntax, pathlib.Path methods, itertools.batched).
**Line length:** 88 characters (matching the Black-compatible default).
**Format:** Generated scripts should be formatted via `uv run ruff format` before submission.

## Pyright Type-Check Settings

Pyright is configured with `typeCheckingMode: "standard"` and `include: ["src", "tests"]`.

**Key implications:**
- Requires type annotations on all function signatures.
- Both source and test files are type-checked.
- Uses `.venv` relative to the config file for third-party type resolution.

All generated functions must have annotated parameters and return types:

```python
def compute(input_path: Path, threshold: float | None = None) -> dict[str, int]:
    ...
```

Avoid `Any` where possible. Use `object` for genuinely unknown types, `TypeVar` for generic functions, and `Protocol` for structural subtyping.

## Import Ordering

Ruff rule **I** (isort) enforces consistent import ordering.
Within each block, imports are alphabetically sorted.

1. Standard library — `os`, `pathlib`, `sys`, `json`, `collections.abc`.
2. Third-party — `click`, `yaml`, `jsonschema`.
3. Local — `lib.shared.*`, `lib.<script_name>.*`.

Separate groups with a blank line:

```python
"""CLI entry point for count-tokens."""

from __future__ import annotations

import json
from pathlib import Path

import click

from lib.shared.files import resolve_path
from lib.count_tokens.core import count_tokens
```

`from __future__ import annotations` is recommended but not enforced.

## Naming Conventions

- **Modules (files)** (`count_tokens.py`, `file_utils.py`): `snake_case`.
- **Packages (directories)** (`lib/count_tokens/`, `lib/shared/`): `snake_case`.
- **Functions** (`count_tokens_in_file()`, `validate_path()`): `snake_case`.
- **Classes** (`TokenCounter`, `FileValidator`): `PascalCase`.
- **Constants** (`WORKSPACE_ROOT`, `DEFAULT_ENCODING`): `UPPER_CASE`.
- **Entry point names (pyproject.toml)** (`count-tokens`, `validate-skill`): `kebab-case`.
- **Test files** (`test_count_tokens.py`): `test_<module>.py`.
- **Test functions** (`test_count_tokens_with_file()`): `test_<descriptive_name>`.
- **Test classes** (`TestCountTokensCLI`): `Test<Feature>`.

## Type Annotation Style

All function signatures in generated code must include type annotations.
Use these conventions:

```python
# Standard annotations
def count_words(text: str, encoding: str = "utf-8") -> int: ...

# Optional and union types (PEP 604, Python 3.10+)
def find_files(glob_pattern: str, root: Path | None = None) -> list[Path]: ...

# Path objects over strings
def process_input(input_path: Path, output_path: Path) -> dict[str, object]: ...

# Typed dictionaries for structured returns
def analyze(data: list[str]) -> dict[str, int]: ...

# Generators for streaming
def read_lines(path: Path) -> Generator[str, None, None]: ...
```

Prefer `pathlib.Path` over `str` for file path parameters.
Prefer `list[X]` over `List[X]`, `dict[K, V]` over `Dict[K, V]`.

## Coverage Exemptions

Use `# pragma: no cover` sparingly and only for these three categories:

1. **`__main__` guard** — The `if __name__ == "__main__": main()` block is exempted by convention.
2. **Unreachable defensive code** — Branches that exist only for type narrowing and cannot be triggered in practice.
3. **Version-gated fallbacks** — Code paths for older Python versions when the target is py312.

All other branches, error paths, and edge cases must be covered by tests.
If `# pragma: no cover` appears outside these three categories, re-examine the test generation rather than exempting coverage.