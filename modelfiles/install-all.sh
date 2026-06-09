#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

for modelfile in "$script_dir"/*.Modelfile; do
  [ -e "$modelfile" ] || continue

  filename="$(basename -- "$modelfile")"
  model_name="${filename%.Modelfile}"
  model_name="${model_name#worker-}"

  echo "Removing existing model: $model_name"
  ollama rm "$model_name" >/dev/null 2>&1 || true

  echo "Installing model: $model_name from $filename"
  ollama create "$model_name" -f "$modelfile"
done
