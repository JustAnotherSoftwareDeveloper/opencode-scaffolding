# Python Style Guide

Every generated script and library module must follow the project's bounded
Google-inspired style policy and type-check rules. Ruff enforces selected structural
rules; human review remains responsible for exceptions and documentation meaning.
These policies are configured in `ruff.toml` and `pyrightconfig.json` at
`scripts/python/`.

## Approved Ruff Profile

Ruff is configured to target Python 3.12 (`py312`) and select these lint categories:

- **E** (pycodestyle errors): Syntax errors, indentation, line breaks.
- **F** (pyflakes): Unused imports, undefined names, duplicate arguments.
- **I** (isort): Import ordering (stdlib, third-party, local).
- **N** (pep8-naming): snake_case functions/variables, PascalCase classes, UPPER_CASE constants.
- **W** (pycodestyle warnings): Trailing whitespace, blank line conventions.
- **UP** (pyupgrade): Modern Python syntax (py312 target).
- **B** (flake8-bugbear): Logical bugs: mutable defaults, bare `except:`, `del` on locals.
- **SIM** (flake8-simplify): Simplify expressions: `if bool(x)` to `if x`, merge nested `if` blocks.
- **ARG** (flake8-unused-arguments): Unused function arguments (suppress with `_` prefix).
- **D** (pydocstyle): Selected docstring checks using Ruff's Google convention, with
  `D400` selected explicitly.

Use Python 3.12 features supported by the `py312` target, such as type parameter
syntax, `pathlib.Path` methods, and `itertools.batched`.

The project style policy sets both Ruff formatter `line-length` and
`lint.pycodestyle.max-line-length` to 80. Keep `E501` active. The `D` rules use
Ruff's Google pydocstyle convention; `D400` is added explicitly to require a period at
the end of a docstring summary.

## Line Length And Formatting

Keep Python source and test lines within 80 characters where practical. Use only narrow,
reviewed exceptions, such as an unavoidable long import or URL, or a line the formatter
cannot wrap below the limit without harming clarity. Keep each exception specific and
explain its justification during review; do not raise the project-wide limit or broadly
suppress `E501`.

Run Ruff formatting and linting as separate checks. Format with `uv run ruff format`
and lint with `uv run ruff check`. Formatting wraps lines on a best-effort basis and
does not replace the active `E501` check; a formatted file may still have a linted
long-line finding. Ruff formatting also does not sort imports; the `I` rules own import
sorting.

Do not enable docstring-code formatting unless it is separately authorized. Formatting
code examples inside a docstring is independent of the prose and documentation rules.

## Docstrings

Use triple-double-quoted docstrings. Start with a concise, single-line summary no longer
than 80 characters, ending in a period. Put any longer explanation after a blank line.
The explicit `D400` selection enforces the local summary-period rule; it is a bounded
policy choice, not a claim that this punctuation rule restates every Google requirement.

Write function and method docstrings when they are public API, nontrivial, or contain
non-obvious logic. Describe caller-visible syntax and behavior rather than narrating
irrelevant implementation details. Add useful `Args:`, `Returns:` or `Yields:`, and
`Raises:` sections when they clarify the interface. Omit sections when the signature or
summary already makes the relevant information clear; do not add empty or repetitive
sections.

Ruff's selected Google pydocstyle rules can check docstring structure, but cannot decide
whether a docstring is needed, whether its account of behavior is accurate, or whether
its interface sections are useful. Review those questions for meaning and caller
relevance.

This is a bounded Google-inspired subset, not full conformance to the Google Python
Style Guide. Only the requirements stated in this guide are adopted as this project's
policy; Ruff's Google convention does not automatically enforce the complete guide.

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
3. Local — `lib.shared.*`, `lib.skill_metadata.*`.

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
- **Test files** (`test_count_tokens.py`): use the `test_` prefix and the tested
  module's `snake_case` name.
- **Test functions** (`test_count_tokens_with_file()`): use the `test_` prefix and a
  descriptive `snake_case` name.
- **Test classes** (`TestCountTokensCLI`): use the `Test` prefix and a descriptive
  `PascalCase` name.

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

- **`__main__` guard** — The `if __name__ == "__main__": main()` block is exempted by convention.
- **Unreachable defensive code** — Branches that exist only for type narrowing and cannot be triggered in practice.
- **Version-gated fallbacks** — Code paths for older Python versions when the target is py312.

All other branches, error paths, and edge cases must be covered by tests.
If `# pragma: no cover` appears outside these three categories, re-examine the test generation rather than exempting coverage.
