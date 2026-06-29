#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=../lib/shared/common.sh
readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/shared/common.sh"

# --- Constants ---
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# --- Exit codes ---
readonly EXIT_SUCCESS=0
readonly EXIT_RUNTIME=1
readonly EXIT_USAGE=2
readonly EXIT_ENVIRONMENT=3

# --- Functions ---

usage() {
  cat >&2 <<EOF
Usage: ${SCRIPT_NAME} [options] <required-arg>

Options:
  -h, --help         Show this help message
  -o, --output FILE  Write output to FILE (default: stdout)
  -v, --verbose      Enable verbose logging

Arguments:
  <required-arg>     Path to input file

Exit codes:
  0  Success
  1  Runtime error
  2  Usage error
  3  Environment error
EOF
  exit "${EXIT_USAGE}"
}

parse_args() {
  local OPTIND
  while getopts ":ho:v-:" opt; do
    case "${opt}" in
      h) usage ;;
      o) OUTPUT_FILE="${OPTARG}" ;;
      v) VERBOSE=1 ;;
      -) case "${OPTARG}" in
           help) usage ;;
           output=*) OUTPUT_FILE="${OPTARG#*=}" ;;
           verbose) VERBOSE=1 ;;
           *) err "Unknown option: --${OPTARG}"; usage ;;
         esac ;;
      \?) err "Unknown option: -${OPTARG}"; usage ;;
      :) err "Option -${OPTARG} requires an argument"; usage ;;
    esac
  done
  shift $((OPTIND - 1))

  # Positional args
  INPUT_FILE="${1:-}"
  if [[ -z "${INPUT_FILE}" ]]; then
    err "Missing required argument: <required-arg>"
    usage
  fi
}

validate_env() {
  require "jq" "jq is required for JSON processing"
}

main() {
  parse_args "$@"
  validate_env

  # --- Script logic here ---
  if [[ ! -f "${INPUT_FILE}" ]]; then
    die "File not found: ${INPUT_FILE}" "${EXIT_RUNTIME}"
  fi

  # Output to stdout
  printf '{"status":"ok","input":"%s"}\n' "${INPUT_FILE}"
}

main "$@"