#!/usr/bin/env bats

setup() {
  # Load assertion libraries if available
  if command -v bats >/dev/null 2>&1; then
    local helper_dir
    helper_dir="$(cd "$(dirname "${BATS_TEST_FILENAME}")/test_helper" && pwd 2>/dev/null || true)"
    if [[ -d "${helper_dir}/bats-support" ]]; then
      load "${helper_dir}/bats-support/load"
    fi
    if [[ -d "${helper_dir}/bats-assert" ]]; then
      load "${helper_dir}/bats-assert/load"
    fi
  fi

  # Determine script directory relative to test file
  SCRIPT_DIR="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../src" && pwd)"
}

@test 'tool-versions: --help exits 2 and prints usage' {
  run bash "${SCRIPT_DIR}/tool-versions.sh" --help
  [[ "${status}" -eq 2 ]]
  [[ "${output}" == *"Usage:"* ]]
  [[ "${output}" == *"tool-versions"* ]]
}

@test 'tool-versions: -h exits 2 and prints usage' {
  run bash "${SCRIPT_DIR}/tool-versions.sh" -h
  [[ "${status}" -eq 2 ]]
  [[ "${output}" == *"Usage:"* ]]
}

@test 'tool-versions: produces valid JSON on stdout' {
  run bash "${SCRIPT_DIR}/tool-versions.sh"
  [[ "${status}" -eq 0 ]]
  # Should be valid JSON with "tools" key
  [[ "${output}" == "{"* ]]
  [[ "${output}" == *'"tools"'* ]]
  [[ "${output}" == *"}" ]]
}

@test 'tool-versions: detects git if available' {
  if ! command -v git >/dev/null 2>&1; then
    skip "git is not installed"
  fi
  run bash "${SCRIPT_DIR}/tool-versions.sh"
  [[ "${status}" -eq 0 ]]
  [[ "${output}" == *'"git"'* ]]
  [[ "${output}" == *"git version"* ]]
}

@test 'tool-versions: --verbose includes meta section' {
  run bash "${SCRIPT_DIR}/tool-versions.sh" --verbose
  [[ "${status}" -eq 0 ]]
  [[ "${output}" == *'"meta"'* ]]
  [[ "${output}" == *'"bash_version"'* ]]
}

@test 'tool-versions: errors on unexpected argument' {
	run bash "${SCRIPT_DIR}/tool-versions.sh" unexpected
	[[ "${status}" -eq 2 ]]
	[[ "${output}" == *"ERROR:"* ]]
}

@test 'tool-versions: errors on unknown option' {
	run bash "${SCRIPT_DIR}/tool-versions.sh" --bogus
	[[ "${status}" -eq 2 ]]
	[[ "${output}" == *"ERROR:"* ]]
}

@test 'tool-versions: output can be parsed by jq' {
  if ! command -v jq >/dev/null 2>&1; then
    skip "jq is not installed"
  fi
  run bash "${SCRIPT_DIR}/tool-versions.sh"
  [[ "${status}" -eq 0 ]]
  # Validate that jq can parse it and extract the tools key
  local parsed
  parsed="$(echo "${output}" | jq -r '.tools | keys | .[]' 2>/dev/null)" || {
    echo "jq parse failed"
    return 1
  }
  [[ -n "${parsed}" ]]
}