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

@test '<script-name>: --help prints usage and exits 2' {
  run bash src/<script-name>.sh --help
  assert_failure
  assert_output --partial 'Usage:'
  assert_output --partial '<script-name>'
}

@test '<script-name>: missing required argument prints error and exits 2' {
  run bash src/<script-name>.sh
  assert_failure
  assert_stderr --partial 'Error:'
}

@test '<script-name>: errors on non-existent input file' {
  run bash src/<script-name>.sh /nonexistent/path
  assert_failure
  assert_stderr --partial 'Error:'
}

@test '<script-name>: processes valid input file' {
  # Create a fixture file
  local input_file="${TEST_TEMP}/input.txt"
  printf 'test data\n' > "${input_file}"

  run bash src/<script-name>.sh "${input_file}"
  assert_success
  assert_output --partial 'status=ok'
}

@test '<script-name>: verbose mode outputs info messages' {
  local input_file="${TEST_TEMP}/input.txt"
  printf 'test data\n' > "${input_file}"

  run bash src/<script-name>.sh -v "${input_file}"
  assert_success
  assert_stderr --partial 'Info:'
}