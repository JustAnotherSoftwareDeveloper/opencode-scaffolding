# Error Handling

Use unified `die()` and `err()` helpers from `lib/shared/common.sh`:

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

Trap pattern for cleanup:

```bash
cleanup() {
  local exit_code=$?
  [[ -n "${TEMP_DIR:-}" && -d "${TEMP_DIR}" ]] && rm -rf "${TEMP_DIR}"
  exit "${exit_code}"
}
trap cleanup EXIT
```

Named exit code constants:

```bash
readonly EXIT_SUCCESS=0
readonly EXIT_RUNTIME=1
readonly EXIT_USAGE=2
readonly EXIT_ENVIRONMENT=3
```