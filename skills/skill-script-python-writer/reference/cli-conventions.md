# CLI Conventions

Every generated script must follow these CLI design patterns.

## Click Argument vs Option Convention

- **When to use**: `@click.argument()` — Required positional input (file path, data source); `@click.option()` — Optional modifiers (output format, filter, verbosity)
- **Example**: `@click.argument()` — `@click.argument("input_path", type=click.Path(exists=True))`; `@click.option()` — `@click.option("--format", default="json")`
- **CLI usage**: `@click.argument()` — `script path/to/file`; `@click.option()` — `script path/to/file --format yaml`
- **Validation**: `@click.argument()` — Use `type=click.Path(exists=True)` for path existence; `@click.option()` — Use `type=click.Choice([...])` for enum options

**Rule of thumb:** If the user must always provide it, make it an argument.
If it has a sensible default, make it an option.

## Output Format Standards

- **Primary result**: `click.echo(json.dumps(result))` — JSON on stdout — Output consumed by another skill (default)
- **Human-readable**: `click.echo(f"Found {n} files")` — plain text on stdout — Output displayed directly to user
- **Progress/info**: `click.echo(message, err=True)` — stderr — Status messages when stdout is structured data
- **Errors**: `click.echo(f"Error: {msg}", err=True)` + `raise SystemExit(1)` — All failure paths

When output is consumed by another skill, emit a single JSON object or array to stdout.
Use `json.dumps()` with `default=str` for non-serializable types.

## Exit Code Conventions

- **Success** (Exit Code 0): Normal completion, output on stdout
- **Runtime error** (Exit Code 1): Unexpected failure, exception, missing resource
- **User error (bad input)** (Exit Code 2): Click built-in for invalid option/argument; explicit `raise SystemExit(2)` for semantic validation
- **Environment error** (Exit Code 3): Missing dependencies, broken configuration, incompatible Python version

Generated scripts do not catch `SystemExit` or `click.ClickException` — these are legitimate exit paths.
Only catch exceptions to produce a clean error message before re-raising as `SystemExit`.

## Error Message Formatting

Error messages follow a consistent pattern: `Error: <human-readable description>`.
Write to stderr via `click.echo(..., err=True)`.
Start with `"Error: "` prefix (capital E, colon, space).
Include the specific cause when available (file name, invalid value).
Do not include Python tracebacks in user-facing output.

## Complete Real-World Example: `count-tokens`

The following example demonstrates all CLI conventions.

```python
"""CLI entry point for count-tokens — count tokens in a text file.

This script is invoked as:
  uv run --project <scripts-python-dir> count-tokens <input-path> [options]

Exit codes:
  0 — Success, token count written to stdout.
  1 — Runtime error (file unreadable, encoding error).
  2 — User error (invalid arguments).
"""

from __future__ import annotations

import json
from pathlib import Path

import click

from lib.shared.files import resolve_path


def count_tokens(text: str) -> int:
    """Return the number of tokens in *text*.

    A token is defined as a whitespace-delimited word.
    """
    if not text.strip():
        return 0
    return len(text.split())


def process_file(input_path: Path, encoding: str = "utf-8") -> dict[str, int]:
    """Read *input_path* and return a token count dict."""
    if not input_path.is_file():
        raise FileNotFoundError(f"Not a file: {input_path}")

    try:
        text = input_path.read_text(encoding=encoding)
    except (UnicodeDecodeError, PermissionError) as exc:
        raise RuntimeError(f"Cannot read {input_path}: {exc}") from exc

    token_count = count_tokens(text)
    return {
        "path": str(input_path.resolve()),
        "tokens": token_count,
        "encoding": encoding,
    }


@click.command()
@click.argument("input_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--encoding", default="utf-8", show_default=True, help="File encoding.")
@click.option("--format", type=click.Choice(["json", "text"]), default="json", help="Output format.")
@click.option("--verbose", is_flag=True, default=False, help="Print diagnostic information to stderr.")
def main(input_path: str, encoding: str, format: str, verbose: bool) -> None:
    """Count tokens in INPUT_PATH and print the result."""
    path = resolve_path(input_path)

    if verbose:
        click.echo(f"Reading: {path}", err=True)
        click.echo(f"Encoding: {encoding}", err=True)

    try:
        result = process_file(path, encoding=encoding)
    except (FileNotFoundError, RuntimeError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc

    if format == "json":
        click.echo(json.dumps(result, default=str))
    else:
        click.echo(f"Tokens: {result['tokens']}")


if __name__ == "__main__":
    main()
```

This example illustrates: docstring contract with invocation pattern and exit codes, type annotations on every function, `from __future__ import annotations`, argument for required path with options for modifiers, separate error classes caught with friendly messages to stderr and non-zero exit, JSON default output with `--format text` for human readers, core logic delegated to lib functions, empty file returning `0` tokens, and `__name__ == "__main__"` guard.
