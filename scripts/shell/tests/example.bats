#!/usr/bin/env bats

load 'setup'

SCRIPT_DIR="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../src" && pwd)"

@test 'example.sh prints example message' {
  run bash "${SCRIPT_DIR}/example.sh"
  assert_success
  assert_output 'example runtime=shell status=ok'
}

@test 'example.sh ignores extra arguments' {
  run bash "${SCRIPT_DIR}/example.sh" --verbose
  assert_success
  assert_output 'example runtime=shell status=ok'
}

@test 'example.sh ignores multiple extra arguments' {
  run bash "${SCRIPT_DIR}/example.sh" foo bar baz
  assert_success
  assert_output 'example runtime=shell status=ok'
}
