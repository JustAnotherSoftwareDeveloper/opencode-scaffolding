# Testing Conventions

Follow conventions in `skill-bash-conventions` (exit-codes, json-output-conventions) for exit code usage and JSON output format expectations in test assertions.

## bats-core Setup

Tests live under `scripts/shell/tests/` with a `.bats` extension. Each source script in `src/` has a corresponding test file.

**Basic test structure:**

```bash
#!/usr/bin/env bats

setup() {
  # Load assertion libraries
  load 'bats-support/load'
  load 'bats-assert/load'

  # Set up temp directory for test fixtures
  TEST_TEMP="$(mktemp -d)"
}

teardown() {
  rm -rf "${TEST_TEMP}"
}

@test 'example: prints expected output' {
  run bash src/example.sh
  assert_success
  assert_output --partial 'status=ok'
}

@test 'example: errors on missing argument' {
  run bash src/example.sh
  assert_failure
  assert_stderr --partial 'Error:'
}
```

## Assertion Libraries

Use the standard bats-core assertion ecosystem, installed system-wide via package manager:

- **`bats-support`** — Helper utilities for other assertion libs. Install: `bats-support` (apt/brew) or `@bats-core/support` (npm).
- **`bats-assert`** — Provides `assert_success`, `assert_failure`, `assert_output`, `assert_stderr`, `assert_line`, `refute_output`. Install: `bats-assert` (apt/brew) or `@bats-core/assert` (npm).
- **`bats-file`** — Provides `assert_file_exist`, `assert_dir_exist`, `assert_not_empty`, `assert_file_contains`. Install: `bats-file` (apt/brew) or `@bats-core/file` (npm).

**Loading in setup:**

```bash
setup() {
  load 'bats-support/load'
  load 'bats-assert/load'
  load 'bats-file/load'
}
```

## Mock Patterns

Mock external commands by manipulating PATH:

```bash
setup() {
  MOCK_DIR="$(mktemp -d)"

  # Mock the 'git' command
  cat > "${MOCK_DIR}/git" <<'MOCK'
#!/usr/bin/env bash
if [[ "$1" == "rev-parse" && "$2" == "--abbrev-ref" && "$3" == "HEAD" ]]; then
  echo "main"
  exit 0
fi
echo "unexpected git call: $*" >&2
exit 1
MOCK
  chmod +x "${MOCK_DIR}/git"
  PATH="${MOCK_DIR}:${PATH}"
}

teardown() {
  rm -rf "${MOCK_DIR}"
}
```

## Fixture Management

Fixtures live under `scripts/shell/fixtures/<script-name>/`. Use `BATS_TEST_DIRNAME` for relative paths:

```bash
@test 'process_json: handles valid input' {
  local fixture="${BATS_TEST_DIRNAME}/../fixtures/process_json/valid.json"
  run bash src/process_json.sh "${fixture}"
  assert_success
}
```

Use temp directories (`mktemp -d`) for writable test fixtures. The `teardown()` function should clean up all temp directories.

## Test Coverage Expectations

Each test file should cover:

1. **`--help` output** — Verify `bash src/<script-name>.sh --help` exits 2 with usage text.
2. **Success path** — Verify normal execution produces correct JSON output on stdout.
3. **Failure path** — Verify error conditions produce `Error:` on stderr and non-zero exit.
4. **Argument validation** — Verify missing required args produce exit 2 with error on stderr.
5. **Edge cases** — Verify empty input, missing files, invalid options, and boundary conditions.

## Local Validation Workflow

Run `make -C scripts/shell check` before committing. This executes:

1. `make deps-check` — Verify shellcheck, shfmt, and bats are installed.
2. `make lint` — Run shellcheck on all shell files.
3. `make format-check` — Check formatting with shfmt without modifying.
4. `make test` — Run the bats-core test suite.
5. `make coverage` — Run bashcov coverage (enforces 100% `fail_under`).
