# Error Handling

## Diagnostic helpers

Use the shared helpers in `lib/shared/common.sh` for three cases: `die()` writes an error to stderr and exits, `err()` writes an error to stderr without exiting, and `info()` writes an informational message to stderr only in verbose mode.

```bash
# Die with error message and exit code
die() {
  local code="${2:-1}"
  printf 'Error: %s\n' "$1" >&2
  exit "${code}"
}

# Print error message without exiting
err() {
  printf 'Error: %s\n' "$*" >&2
}

# Print info message to stderr (for verbose mode)
info() {
  if [[ -n "${VERBOSE:-}" ]]; then
    printf 'Info: %s\n' "$*" >&2
  fi
}
```

## Cleanup trap

When cleanup succeeds or is skipped, this `EXIT` trap exits with the status captured when it starts; under `errexit`, a cleanup failure can stop it before that explicit exit:

```bash
cleanup() {
  local exit_code=$?
  [[ -n "${TEMP_DIR:-}" && -d "${TEMP_DIR}" ]] && rm -rf "${TEMP_DIR}"
  exit "${exit_code}"
}
trap cleanup EXIT
```

## Exit code constants

Define named constants for success, runtime, usage, and environment exit codes:

```bash
readonly EXIT_SUCCESS=0
readonly EXIT_RUNTIME=1
readonly EXIT_USAGE=2
readonly EXIT_ENVIRONMENT=3
```
