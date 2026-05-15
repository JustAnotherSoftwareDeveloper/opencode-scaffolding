# Python Scripts for OpenCode

This directory contains Python automation scripts for OpenCode skills.

## Testing

To run the test suite:

```bash
# Install development dependencies
uv sync --dev

# Run all tests
uv run --project scripts/python pytest scripts/python/tests/

# Run specific test file
uv run --project scripts/python pytest scripts/python/tests/test_runbook_validation.py

# Run with verbose output
uv run --project scripts/python pytest scripts/python/tests/test_runbook_validation.py -v
```

## Available Commands

- `validate-runbook` - Validate runbooks in v1 JSON or v2 TOON format
- `init-runbook-state` - Initialize runbook state files
- `validate-json` - Validate JSON files
- `validate-yaml` - Validate YAML files

## Runbook Format Support

This project supports both:
- v1 JSON format: `.runbooks/<id>/runbook.json`
- v2 TOON format: `.runbooks/<id>/main.toon` with referenced step files in `steps/<step-id>.toon`

## Testing Coverage

The test suite covers:
- Valid v2 TOON runbook parsing and validation
- Negative invariant cases (cycles, missing files, ID mismatches, etc.)
- Legacy v1 JSON compatibility
- State initialization compatibility