# Error Handling And Testing

Validate every public mode and failure boundary.

## Exit Code Checks

- Expect `0` for successful atomic publication.
- Expect `1` for runtime, model, diagnostics, or filesystem failures.
- Expect `2` for malformed input, inventory, token, path, or argument failures.
- Require empty success stdout on every failure.
- Require no task or partial diagnostics file on every failure.

## Offline Tests

1. Inject rankers and frozen transports.
2. Cover Q8 and Q4 identity checks.
3. Cover exact request JSON.
4. Cover yes/no parsing and missing-label clipping.
5. Cover stable selection and low confidence.
6. Cover caller-root inventory authorization.
7. Cover complete-prompt token boundaries.
8. Cover atomic diagnostics bundles.
9. Cover lexical rollback without model setup.

## Native Smoke Tests

1. Collect one frozen caller-root inventory.
2. Remove generated `skills` fields from a previous task packet.
3. Run Qwen generation into a temporary output directory.
4. Validate the generated packet without auto-fix.
5. Confirm diagnostics contain one record per task.
6. Compare selected names only against the frozen inventory.
7. Preserve the smoke report outside normal tests.

## Validation Commands

```bash
uv run --directory ~/.config/opencode/scripts/python pytest
uv run --directory ~/.config/opencode/scripts/python ruff check .
uv run --directory ~/.config/opencode/scripts/python pyright
```
