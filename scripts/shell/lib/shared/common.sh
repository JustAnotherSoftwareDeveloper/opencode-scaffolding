#!/usr/bin/env bash
#
# lib/shared/common.sh — shared error handling, logging, and cleanup utilities
#
# This library provides exit-code constants, logging functions (die/err/info),
# a tool-dependency checker (require), and a cleanup-trap pattern.
# It does NOT set any `set` flags — the caller is responsible for that.
# Sourcing this file registers the cleanup trap on EXIT automatically.

# ---------------------------------------------------------------------------
# Exit code constants
# ---------------------------------------------------------------------------
# shellcheck disable=SC2034  # constants exported for callers
readonly EXIT_SUCCESS=0
readonly EXIT_RUNTIME=1
readonly EXIT_USAGE=2
readonly EXIT_ENVIRONMENT=3

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

# die MESSAGE [EXIT_CODE]
#   Print MESSAGE to stderr prefixed with "ERROR: " and exit with EXIT_CODE.
#   EXIT_CODE defaults to EXIT_RUNTIME (1).
die() {
	local msg="$1"
	local code="${2:-$EXIT_RUNTIME}"
	printf 'ERROR: %s\n' "$msg" >&2
	exit "$code"
}

# err MESSAGE [MESSAGE ...]
#   Print MESSAGE(s) to stderr prefixed with "ERROR: ".
err() {
	printf 'ERROR: %s\n' "$*" >&2
}

# info MESSAGE [MESSAGE ...]
#   Print MESSAGE(s) to stderr prefixed with "INFO: ", but only when the
#   __verbose environment variable is set to a non-empty value.
info() {
	if [ -n "${__verbose:-}" ]; then
		printf 'INFO: %s\n' "$*" >&2
	fi
}

# ---------------------------------------------------------------------------
# Tool dependency checking
# ---------------------------------------------------------------------------

# require COMMAND [COMMAND ...]
#   Verify that each COMMAND is available on PATH.  Exit with
#   EXIT_ENVIRONMENT (3) if any command is missing.
require() {
	local cmd
	for cmd; do
		if ! command -v "$cmd" >/dev/null 2>&1; then
			die "required command not found: $cmd" "$EXIT_ENVIRONMENT"
		fi
	done
}

# ---------------------------------------------------------------------------
# Cleanup trap pattern
# ---------------------------------------------------------------------------

# __cleanup_tasks holds the list of registered cleanup commands (or function
# names).  It is intentionally a double-underscore name to signal "internal".
__cleanup_tasks=()

# register_cleanup TASK [TASK ...]
#   Register one or more cleanup tasks.  Each task is a shell command string
#   or function name that will be evaluated at cleanup time.
register_cleanup() {
	local task
	for task; do
		__cleanup_tasks+=("$task")
	done
}

# cleanup
#   Execute all registered cleanup tasks in reverse registration order (LIFO).
#   Individual task failures are swallowed so that every task gets a chance
#   to run.  The task list is cleared afterwards.
cleanup() {
	local task
	local i
	for ((i = ${#__cleanup_tasks[@]} - 1; i >= 0; i--)); do
		task="${__cleanup_tasks[$i]}"
		eval "$task" 2>/dev/null || true
	done
	__cleanup_tasks=()
}

# Automatically register the cleanup handler on EXIT when this file is
# sourced.  Callers may override this trap by calling trap themselves.
trap cleanup EXIT
