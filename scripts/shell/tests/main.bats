#!/usr/bin/env bats

load 'setup'

SCRIPT_DIR="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../src" && pwd)"

@test 'main.sh prints placeholder message' {
  run bash "${SCRIPT_DIR}/main.sh"
  assert_success
  assert_output 'scripts/shell placeholder entry point'
}

@test 'main.sh ignores arbitrary arguments' {
  run bash "${SCRIPT_DIR}/main.sh" --help
  assert_success
  assert_output 'scripts/shell placeholder entry point'
}

@test 'main.sh ignores multiple positional arguments' {
  run bash "${SCRIPT_DIR}/main.sh" foo bar baz
  assert_success
  assert_output 'scripts/shell placeholder entry point'
}
