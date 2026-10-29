# Verification Practices

Verification checks by task type.

## File Creation Tasks

- File exists at the expected path.
- File is non-empty.
- The relevant parser accepts the file.
- Naming and directory structure follow project conventions.

## File Modification Tasks

- Diff inspection confirms all expected changes are present.
- Diff inspection finds no unintended changes elsewhere in the file.
- File still parses without errors.
- When backward compatibility is required, existing exports, interfaces, and public API surface remain intact.

## Refactoring Tasks

- Existing tests still pass.
- Public API or interface contracts are unchanged.
- No dead code or orphaned imports remain.
- Linter reports no new warnings.
- Build or type-check succeeds.

## Testing Tasks

- All new tests pass.
- Code coverage meets the project threshold (if applicable).
- No flaky tests are introduced (tests are deterministic and use no shared mutable state).
- Tests verify the intended behavior, not implementation details.

## Configuration Tasks

- Configuration file is valid YAML, JSON, TOML, or the expected format.
- Configuration references existing resources, paths, and identifiers.
- Syntax check passes (e.g., `python -c "import yaml; yaml.safe_load(open(...))"`).
- If the configuration activates a feature, that feature's tests pass.
