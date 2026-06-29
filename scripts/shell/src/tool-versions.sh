#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=../lib/shared/common.sh
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR
source "${SCRIPT_DIR}/../lib/shared/common.sh"

# shellcheck source=../lib/tool-versions/core.sh
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/../lib/tool-versions/core.sh"

# --- Constants ---
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
readonly SCRIPT_NAME

# --- Options ---
VERBOSE=0

# --- Functions ---

usage() {
	cat >&2 <<EOF
Usage: ${SCRIPT_NAME} [options]

Detect common development CLI tools and report their versions as JSON.

Options:
  -h, --help         Show this help message and exit
  -v, --verbose      Include environment details (e.g., PATH entries)

Output:
  JSON object on stdout with tool names as keys and version strings as values.

Exit codes:
  0  Success (all tools found or not — detection is informational)
  1  Runtime error
  2  Usage error (invalid option)
  3  Environment error (unsupported shell)

Example:
  ${SCRIPT_NAME}
  ${SCRIPT_NAME} --verbose
EOF
	exit "${EXIT_USAGE}"
}

parse_args() {
	local OPTIND
	while getopts ":hv-:" opt; do
		case "${opt}" in
		h) usage ;;
		v) VERBOSE=1 ;;
		-) case "${OPTARG}" in
			help) usage ;;
			verbose) VERBOSE=1 ;;
			*)
				err "Unknown option: --${OPTARG}"
				usage
				;;
			esac ;;
		\?)
			err "Unknown option: -${OPTARG}"
			usage
			;;
		:)
			err "Option -${OPTARG} requires an argument"
			usage
			;;
		esac
	done
	shift $((OPTIND - 1))

	if [[ $# -gt 0 ]]; then
		err "Unexpected argument: $1"
		usage
	fi
}

main() {
	parse_args "$@"

	# Build JSON output via lib functions
	local json
	json="$(tool_versions::report "${VERBOSE}")"

	printf '%s\n' "${json}"
}

main "$@"
