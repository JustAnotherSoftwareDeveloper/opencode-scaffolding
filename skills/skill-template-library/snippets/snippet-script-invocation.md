# Script Invocation

**Script invocation:**

```shell
# Resolve scripts directory (project-local first, global fallback; see A.3)
SCRIPTS_PYTHON="${OPENCODE_SCRIPTS_PYTHON:-$PWD/.opencode/scripts/python}"
SCRIPTS_PYTHON="${SCRIPTS_PYTHON:-$HOME/.config/opencode/scripts/python}"
uv run --directory "$SCRIPTS_PYTHON" <entry-point> [args]
```

- **Capture stdout** as structured output (JSON preferred).
- **Check exit code** — non-zero means BLOCKED.
- **Parse output** and validate against contract.
- **Handle empty output** as a valid edge case where applicable.
