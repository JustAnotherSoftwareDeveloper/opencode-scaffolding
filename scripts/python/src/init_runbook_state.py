from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lib.json_validation import JsonValidationError, validate_json_path
from lib.runbook_state import HARNESS_ROOT, seed_runbook_state
from lib.runbook_toon import load_runbook, RunbookLoadError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Initialize a runbook's state directory from a runbook file (v1 JSON or v2 TOON format).")
    parser.add_argument("runbook_file", help="Path to the runbook file to validate and seed state from (runbook.json for v1, main.toon for v2).")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        runbook_path = Path(args.runbook_file).resolve()

        # Preserve the legacy v1 JSON Schema gate before using the normalized
        # loader. V2 TOON runbooks are validated by parser-backed invariants in
        # lib.runbook_toon; no v2 JSON Schema exists by design.
        if runbook_path.name == "runbook.json":
            runbook_schema_path = HARNESS_ROOT / "skills/runbook/schema.json"
            validate_json_path(runbook_path, runbook_schema_path)

        # Use the normalized loader that handles both v1 and v2 formats.
        result = load_runbook(runbook_path)
        runbook_data = result.data
        
        # Validate that the runbook file is in the correct location:
        # .runbooks/<runbook_id>/runbook.json or .runbooks/<runbook_id>/main.toon
        if runbook_path.parent.parent.name != ".runbooks":
            print(
                f"Error: Runbook file {runbook_path} must be located at .runbooks/<runbook_id>/runbook.json or .runbooks/<runbook_id>/main.toon so relative state_dir paths resolve safely.",
                file=sys.stderr,
            )
            return 1

        runbook_id = runbook_data.get("id")
        if not runbook_id:
            print(f"Error: Runbook file {args.runbook_file} does not contain an 'id' field.", file=sys.stderr)
            return 1

        if runbook_path.parent.name != runbook_id:
            print(
                f"Error: Runbook directory name '{runbook_path.parent.name}' must match runbook id '{runbook_id}'.",
                file=sys.stderr,
            )
            return 1
        
        # Get the state directory from the runbook
        state_dir_path = runbook_data.get("state_dir")
        if not state_dir_path:
            print(f"Error: Runbook file {args.runbook_file} does not contain a 'state_dir' field.", file=sys.stderr)
            return 1

        expected_state_dir = f"../../.state/{runbook_id}/"
        if state_dir_path != expected_state_dir:
            print(
                f"Error: Runbook state_dir must be '{expected_state_dir}' so state keys off the runbook id; got '{state_dir_path}'.",
                file=sys.stderr,
            )
            return 1
            
        # Resolve the state directory relative to the runbook file
        state_dir = runbook_path.parent / state_dir_path
        state_dir = state_dir.resolve()
        
        # Check if the directory is empty or absent
        if state_dir.exists() and any(state_dir.iterdir()):
            print(f"Error: Target state directory {state_dir} already exists and is not empty.", file=sys.stderr)
            return 1
            
        # Create the state directory if it doesn't exist
        state_dir.mkdir(parents=True, exist_ok=True)
        
        # Seed the state directory
        seed_runbook_state(runbook_data, runbook_path, state_dir)
        
        print(f"Successfully initialized state directory: {state_dir}")
        return 0
        
    except JsonValidationError as exc:
        print(f"init-runbook-state: {exc}", file=sys.stderr)
        return 1
    except RunbookLoadError as exc:
        print(f"init-runbook-state: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"init-runbook-state: Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
