# Python Scripts

Python helpers use uv in non-package project mode.

## Layout

- `src/`: executable Python entry points.
- `lib/`: shared modules imported by scripts in `src/`.

## Examples

```bash
uv run --directory scripts/python --no-sync src/example.py
```

The example script runs `src/example.py`, which imports `lib/example.py` by adding the workspace root to `sys.path` at runtime. Keep scripts dependency-free unless a helper explicitly needs reviewed dependencies.
