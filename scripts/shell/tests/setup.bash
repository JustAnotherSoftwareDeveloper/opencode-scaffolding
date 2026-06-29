#!/usr/bin/env bash

# setup.bash — shared bats test setup
#
# Provides setup() and teardown() for all bats test files under tests/.
# Loads bats-assert, bats-support, and bats-file helper libraries from
# system-installed paths (/usr/lib/bats/). These are provided by the
# apt packages bats-assert, bats-support, and bats-file.
#
# Source from a .bats file:
#   load 'setup'

# Determine this script's directory at source-time so that
# ${BASH_SOURCE[0]} still works before any function context.
SETUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

setup() {
  # System-installed bats helper library directories (apt packages)
  local bats_support_dir="/usr/lib/bats/bats-support"
  local bats_assert_dir="/usr/lib/bats/bats-assert"
  local bats_file_dir="/usr/lib/bats/bats-file"

  if [[ -d "${bats_support_dir}" ]]; then
    load "${bats_support_dir}/load"
  fi
  if [[ -d "${bats_assert_dir}" ]]; then
    load "${bats_assert_dir}/load"
  fi
  if [[ -d "${bats_file_dir}" ]]; then
    load "${bats_file_dir}/load"
  fi

  # Create a per-test temp directory for test artifacts
  BATS_TEST_TMPDIR="$(mktemp -d)"
  export BATS_TEST_TMPDIR
}

teardown() {
  # Clean up the per-test temp directory
  if [[ -n "${BATS_TEST_TMPDIR:-}" && -d "${BATS_TEST_TMPDIR}" ]]; then
    rm -rf "${BATS_TEST_TMPDIR}"
  fi
}