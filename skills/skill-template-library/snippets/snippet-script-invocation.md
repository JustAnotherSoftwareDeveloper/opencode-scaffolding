# Script Invocation

## Decision Criteria: When to Use Each Runtime

Choose a script runtime based on objective criteria. Scripts are appropriate when work is deterministic, repeatable, token-intensive, or has well-defined I/O.

### Python (Default)

Use Python when the work:

1. Is **deterministic** — produces identical output for identical input.
   - Example: parsing YAML, validating JSON schema, computing diffs.
2. Is **repeatable** — the same operation runs many times with different inputs.
   - Example: collecting metadata across many skill directories, transforming batch data.
3. Is **token-intensive** — the LLM reasoning cost exceeds the script's execution cost.
   - Example: iterating over hundreds of files, performing regex transformations at scale.
4. Has **well-defined I/O** — inputs and outputs map cleanly to CLI arguments, stdin, stdout, or files.
   - Example: a click CLI that reads a file path and writes a processed file.
5. Benefits from **library dependencies** — PyYAML, jsonschema, lxml, or other Python packages provide reliable functionality.
   - Example: validating a YAML file against a JSON Schema.

**Do NOT delegate to a script when:**
- Work requires judgment or creativity — LLM reasoning is the correct tool.
- Work involves ambiguous or variable inputs — the I/O shape changes per invocation.
- Work is a one-off with no reuse — the overhead of creating a script exceeds the tokens it saves.
- Work requires adaptive decision-making — the LLM must decide the next step based on partial results.

### Node (TypeScript/Bun)

Select Node only when the core logic requires a Node-specific library (remark, mdast, babel, typescript) and no mature Python equivalent exists.

### Shell

Use Shell for:
- Simple file operations with standard Unix tools.
- Platform-level orchestration already expressed as Make targets.
- Scripts that are thin wrappers around existing CLI tools.

## Invocation Instructions

### Python Invocation

```shell
uv run --directory ~/.config/opencode/scripts/python <entry-point> [args]
```

**Directory layout conventions:**
- `src/cli/` — CLI entry points, using click decorators.
- `src/lib/` — Library logic, organized by domain.
- `tests/` — Tests, using pytest with CliRunner for CLI integration tests.
- Coverage target: 100% (`fail_under = 100` in pyproject.toml).
- Non-interactive; exit non-zero on failure; errors to stderr.

### Node Invocation

```shell
bun run --cwd ~/.config/opencode/scripts/node <script-name> [args]
```

**Directory layout conventions:**
- `src/cli/<script-name>.ts` — CLI entry points, using cleye.
- `src/lib/<script-name>/` — Per-script library packages.
- `src/lib/shared/` — Shared utilities for cross-script use.
- `tests/<script-name>.test.ts` — Unit tests.
- `tests/<script-name>.cli.test.ts` — CLI integration tests.
- `package.json`, `tsconfig.json`, `biome.json` — Tooling configuration.
- Non-interactive; exit non-zero on failure; errors to stderr.

### Shell Invocation

```shell
make -C ~/.config/opencode/scripts/shell <target> [args]
```

**Directory layout conventions:**
- `lib/` — Reusable shell libraries (functions sourced by entry-point scripts).
- `src/` — Executable entry-point scripts (shebang-based, `set -euo pipefail`).
- `Makefile` — Central Makefile defining targets for all entry-point scripts.
- Scripts target `/bin/bash` with `set -euo pipefail` for strict error handling.
- Non-interactive; exit non-zero on failure; errors to stderr.

## Output Handling

- **Capture stdout** as structured output (JSON preferred).
- **Check exit code** — non-zero means BLOCKED.
- **Parse output** and validate against contract.
- **Handle empty output** as a valid edge case where applicable.