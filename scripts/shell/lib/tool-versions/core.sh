# shellcheck shell=bash
#
# lib/tool-versions/core.sh — tool version detection library
#
# Provides functions to detect and report versions of common development
# CLI tools.  Designed to be sourced by src/tool-versions.sh.
#

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Ordered list of tool definitions: name|version_command|version_extract_pattern
# Each entry is space-separated: tool_name get_version_command
# We use this array approach for bash 3.2+ compatibility.
readonly TOOL_VERSIONS_DEFINITIONS=(
	"git|git --version 2>/dev/null | head -1"
	"jq|jq --version 2>/dev/null"
	"shellcheck|shellcheck --version 2>/dev/null | head -1"
	"shfmt|shfmt --version 2>/dev/null"
	"bats|bats --version 2>/dev/null"
	"node|node --version 2>/dev/null"
	"python3|python3 --version 2>/dev/null 2>&1"
)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

# _tool_versions::sanitize VALUE
#   Escape characters unsafe for JSON strings: backslash, double-quote,
#   newline, tab, carriage-return.  Output on stdout.
_tool_versions::sanitize() {
	local str="$1"
	# Escape backslashes first, then double quotes, then control chars
	str="${str//\\/\\\\}"
	str="${str//\"/\\\"}"
	# Remove/replace newlines and other control characters
	str="${str//$'\n'/\\n}"
	str="${str//$'\r'/\\r}"
	str="${str//$'\t'/\\t}"
	printf '%s' "${str}"
}

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

# tool_versions::detect
#   Output one line per detected tool in the format:
#     tool_name|sanitized_version
#   Only tools that are found on PATH are included.
tool_versions::detect() {
	local entry tool_name version_cmd version_line sanitized

	for entry in "${TOOL_VERSIONS_DEFINITIONS[@]}"; do
		tool_name="${entry%%|*}"
		version_cmd="${entry#*|}"

		# Skip if tool is not on PATH
		if ! command -v "${tool_name}" >/dev/null 2>&1; then
			continue
		fi

		# Capture version string
		version_line="$(eval "${version_cmd}" 2>/dev/null)" || version_line=""

		if [[ -n "${version_line}" ]]; then
			sanitized="$(_tool_versions::sanitize "${version_line}")"
			printf '%s|%s\n' "${tool_name}" "${sanitized}"
		fi
	done
}

# tool_versions::report VERBOSE
#   Produce a complete JSON report of all detected tools.
#   If VERBOSE is non-zero, include additional context.
tool_versions::report() {
	local verbose="${1:-0}"

	# Open JSON object
	printf '{\n'

	# "tools" object
	printf '  "tools": {\n'

	local first=1
	local name version_line

	while IFS='|' read -r name version_line; do
		if [[ "${first}" -eq 1 ]]; then
			first=0
		else
			printf ',\n'
		fi
		printf '    "%s": "%s"' "${name}" "${version_line}"
	done < <(tool_versions::detect)

	printf '\n  }'

	# Optional verbose metadata
	if [[ "${verbose}" -ne 0 ]]; then
		printf ',\n  "meta": {\n'
		printf '    "shell": "%s",\n' "$(_tool_versions::sanitize "${SHELL:-}")"
		printf '    "script_dir": "%s",\n' "$(_tool_versions::sanitize "${SCRIPT_DIR:-}")"
		printf '    "bash_version": "%s"\n' "$(_tool_versions::sanitize "${BASH_VERSION:-}")"
		printf '  }'
	fi

	# Close JSON object
	printf '\n}\n'
}
