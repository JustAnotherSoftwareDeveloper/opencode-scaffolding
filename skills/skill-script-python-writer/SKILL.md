---
name: skill-script-python-writer
description: "Use when generating deterministic Python scripts from skill requirements, including CLI entry points, library modules, tests, and pyproject.toml registration."
class: operation
---

# Skill Script Python Writer

## Normalize Input

Map invocation context to one internal input object.
Define these required fields:

- **Script name** — kebab-case entry point name (e.g., `count-tokens`).
- **Purpose** — What the script computes or processes.
- **Input contract** — CLI arguments, stdin format, or file paths the script reads.
- **Output contract** — stdout format (JSON preferred), exit codes, stderr behavior.
- **Dependencies** — Python packages required.
- **Skill consumers** — Which skills will invoke this script.

`BLOCKED: Missing script name — provide a kebab-case entry point name.`
`BLOCKED: Missing purpose — describe what the script computes or processes.`
`BLOCKED: Missing input contract — define CLI arguments, stdin format, or file paths.`

## Procedure

Each step is one imperative action.
Do not delegate sub-tasks.

1. **Parse requirements** — Extract script name, purpose, input/output contracts, dependencies, and skill consumers from the normalized input.
   Validate script name is kebab-case.
   Validate dependencies exist in `pyproject.toml` or add them.

2. **Generate CLI entry point** — Write `src/cli/<script_name>.py` with a click command, typed arguments and options, JSON stdout output, and `Error:` prefix to stderr.
   Follow conventions in `./reference/cli-conventions.md`.

3. **Generate lib modules** — Write `src/lib/<script_name>/__init__.py` and `src/lib/<script_name>/core.py` with typed function signatures, pathlib.Path over str, and imports from `lib.shared.*` where applicable.
   Follow conventions in `./reference/python-style-guide.md` and `./reference/shared-lib-rules.md`.

4. **Register entry point in pyproject.toml** — Add `<script-name> = "cli.<script_name>:main"` under `[project.scripts]`.
   Ensure hatchling packages includes `src/cli`, `src/lib`, and `src/lib/shared` in `[tool.hatch.build.targets.wheel]`.

5. **Run validation** — Execute lint, type check, tests, coverage, and `--help` verification.
   Report `BLOCKED: <step> failed — <details>` on any failure.

## Self-Validation

Each check is a yes/no assertion.

- Lint passes — `uv run ruff check src/cli/<script_name>.py src/lib/<script_name>/` exits zero.
- Type check passes — `uv run pyright src/cli/<script_name>.py` exits zero.
- Tests pass — `uv run pytest tests/test_<script_name>.py tests/test_<script_name>_cli.py -v` exits zero.
- Coverage >= 100% — `uv run pytest --cov --cov-fail-under=100` exits zero.
- Entry point `--help` works — `uv run --directory $SCRIPTS_PYTHON <script-name> --help` exits zero.

## Expected Output

One or more files under `scripts/python/`:

- `src/cli/<script_name>.py` — click CLI entry point with typed arguments, JSON output, and error handling.
- `src/lib/<script_name>/__init__.py` — Library package init.
- `src/lib/<script_name>/core.py` — Core logic module with typed signatures.
- `tests/test_<script_name>.py` — pytest unit tests for lib modules.
- `tests/test_<script_name>_cli.py` — CLI integration tests via CliRunner.

`pyproject.toml` entry point registered under `[project.scripts]`.

## Docs

See `./reference/README.md` for the reference file index.