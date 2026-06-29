#!/usr/bin/env bash
#
# lib/shared/io.sh — JSON I/O helpers and temp directory management
#
# This library provides read_json_field() for extracting values from JSON,
# write_json() for constructing JSON output, and ensure_temp_dir() for
# managing a temporary directory with automatic cleanup.
# It does NOT set any `set` flags — the caller is responsible for that.
# If common.sh has not been sourced yet, this file sources it automatically
# so that logging and cleanup primitives are available.

# ---------------------------------------------------------------------------
# Auto-source common.sh if not already loaded
# ---------------------------------------------------------------------------

if ! declare -F die >/dev/null 2>&1; then
	# shellcheck source=lib/shared/common.sh
	command . "$(dirname "${BASH_SOURCE[0]}")/common.sh"
fi

# ---------------------------------------------------------------------------
# JSON field extraction
# ---------------------------------------------------------------------------

# read_json_field FIELD FILE
#   Extract the value of a top-level FIELD from FILE.
#   Tries jq first; falls back to grep/sed.
#   Outputs the value on stdout.
#   Returns 0 on success, 1 if field is not found / empty, 2 if file is
#   missing.
read_json_field() {
	local field="$1"
	local file="$2"

	if [ ! -f "$file" ]; then
		err "read_json_field: file not found: $file"
		return 2
	fi

	# ---- jq path (preferred) ----
	if command -v jq >/dev/null 2>&1; then
		local val
		val="$(jq -r --arg f "$field" '.[$f] // empty' "$file" 2>/dev/null)" || return 1
		# jq outputs an empty string for both a missing field and an
		# explicitly empty string.  Differentiate by checking the type:
		if [ -z "$val" ]; then
			local typ
			typ="$(jq -r --arg f "$field" '.[$f] | type' "$file" 2>/dev/null)"
			# If the type is "null" the field genuinely doesn't exist.
			# If it's "string" the field exists but is the empty string.
			if [ "$typ" = "null" ]; then
				return 1
			fi
		fi
		printf '%s\n' "$val"
		return 0
	fi

	# ---- grep/sed fallback ----
	# Match:  "field":  <value>
	# Handles simple string, numeric, and boolean values.  Does NOT
	# handle nested objects or arrays.
	if grep -q "\"${field}\":" "$file" 2>/dev/null; then
		local raw
		raw="$(grep "\"${field}\":" "$file" 2>/dev/null |
			head -1 |
			sed 's/.*"'"${field}"'"[[:space:]]*:[[:space:]]*//')"
		# Strip trailing comma
		raw="${raw%,}"
		# Strip surrounding double-quotes if the value is a string
		case "$raw" in
		\"*\")
			raw="${raw#\"}"
			raw="${raw%\"}"
			;;
		esac
		if [ -n "$raw" ]; then
			printf '%s\n' "$raw"
			return 0
		fi
	fi

	return 1
}

# ---------------------------------------------------------------------------
# JSON construction
# ---------------------------------------------------------------------------

# write_json [KEY VALUE ...]
#   Construct a flat JSON object from KEY/VALUE pairs and write it to
#   stdout.  Each pair is a key followed by its value.  All values are
#   treated as strings (quoted).  Backslashes and double-quotes in values
#   are escaped.
#   Returns 0 on success, 1 on odd-argument error.
write_json() {
	if [ $# -eq 0 ]; then
		printf '{}\n'
		return 0
	fi

	if [ $(($# % 2)) -ne 0 ]; then
		err "write_json: odd number of arguments (expected key/value pairs)"
		return 1
	fi

	printf '{'
	local first=1
	local key
	local val
	while [ $# -ge 2 ]; do
		[ "$first" -eq 0 ] && printf ','
		first=0
		key="$1"
		val="$2"
		shift 2
		# Escape backslashes first, then double-quotes
		val="${val//\\/\\\\}"
		val="${val//\"/\\\"}"
		printf '"%s":"%s"' "$key" "$val"
	done
	printf '}\n'
}

# ---------------------------------------------------------------------------
# Temp directory management
# ---------------------------------------------------------------------------

# ensure_temp_dir [PREFIX]
#   Create a temporary directory, print its absolute path to stdout, and
#   register it for automatic removal on EXIT (via common.sh's cleanup
#   trap).  PREFIX defaults to "opencode".
#   Returns exit code of mktemp or mkdir.
ensure_temp_dir() {
	local prefix="${1:-opencode}"
	local temp_dir

	if command -v mktemp >/dev/null 2>&1; then
		temp_dir="$(mktemp -d "/tmp/${prefix}.XXXXXX")" || return 1
	else
		temp_dir="/tmp/${prefix}.$$"
		mkdir -p "$temp_dir" || return 1
	fi

	register_cleanup "rm -rf '${temp_dir}'"
	printf '%s\n' "$temp_dir"
}
