# Shell Scripts

Shell helpers are invoked through `Makefile` targets from the workspace root.

## Layout

- `src/`: executable shell entry points.
- `lib/`: shared shell functions sourced by scripts in `src/`.

## Examples

```bash
make -C scripts/shell help
make -C scripts/shell example
```

The example target runs `src/example.sh`, which sources `lib/example.sh`.
