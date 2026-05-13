#!/usr/bin/env bash

print_example_message() {
  local runtime="${1:?runtime is required}"
  printf 'example runtime=%s status=ok\n' "${runtime}"
}
