#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/example.sh
# shellcheck disable=SC1091
source "${script_dir}/../lib/example.sh"

print_example_message "shell"
