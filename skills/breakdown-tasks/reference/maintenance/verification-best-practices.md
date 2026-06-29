# Verification Practices

Verification checks by task type.

## File Creation Tasks

- File exists at the expected path.
- File is non-empty.
- File syntax is valid (parseable by the relevant parser).
- File follows project conventions (naming, directory structure).

## File Modification Tasks

- All expected changes are present (diff inspection).
- No unintended changes to other parts of the file.
- File still parses without errors.
- Existing exports, interfaces, or public API surface remain intact (if preserving backward compatibility).

## Refactoring Tasks

- Existing tests still pass.
- Public API or interface contracts are unchanged.
- No dead code or orphaned imports remain.
- Linter passes with zero new warnings.
- Build or type-check passes.

## Testing Tasks

- All new tests pass.
- Code coverage meets the project threshold (if applicable).
- No flaky test introductions (tests are deterministic, no shared mutable state).
- Tests verify the intended behavior, not implementation details.

## Configuration Tasks

- Configuration file is valid YAML, JSON, TOML, or whatever format is expected.
- Configuration references existing resources, paths, and identifiers.
- Syntax check passes (e.g., `python -c "import yaml; yaml.safe_load(open(...))"`).
- If the configuration activates a feature, that feature's tests pass.
