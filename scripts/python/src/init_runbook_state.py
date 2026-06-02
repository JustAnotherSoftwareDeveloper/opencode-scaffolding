from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lib.runbook_state import HARNESS_ROOT, seed_runbook_state
from lib.runbook_xml import RunbookLoadError, load_runbook


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Initialize runbook state from a runbook file (v3 XML target, v2 XML transitional, or legacy v1 JSON).")
    parser.add_argument("runbook_file", help="Path to main.xml (v3/v2) or legacy runbook.json.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        runbook_path = Path(args.runbook_file).resolve()
        if runbook_path.parent.parent.name != ".runbooks":
            print(f"Error: Runbook file {runbook_path} must be located at .runbooks/<runbook_id>/main.xml or .runbooks/<runbook_id>/runbook.json.", file=sys.stderr)
            return 1

        if runbook_path.name == "runbook.json":
            schema_path = HARNESS_ROOT / "skills/runbook/schema.json"
            if schema_path.exists():
                from lib.json_validation import validate_json_path

                validate_json_path(runbook_path, schema_path)

        result = load_runbook(runbook_path, require_workspace_xml=False)
        runbook_data = result.data
        runbook_id = runbook_data.get("id")
        if not runbook_id:
            print(f"Error: Runbook file {args.runbook_file} does not contain an 'id' field.", file=sys.stderr)
            return 1
        if runbook_path.parent.name != runbook_id:
            print(f"Error: Runbook directory name '{runbook_path.parent.name}' must match runbook id '{runbook_id}'.", file=sys.stderr)
            return 1

        if result.format_version == 3:
            seed_runbook_state(runbook_data, runbook_path)
            state_path = runbook_path.parent / runbook_data.get("state", "state.xml")
            print(f"Successfully initialized runbook-local state: {state_path}")
            return 0

        state_dir_path = runbook_data.get("state_dir")
        if not state_dir_path:
            print(f"Error: Runbook file {args.runbook_file} does not contain a 'state_dir' field.", file=sys.stderr)
            return 1
        expected_state_dir = f"../../.state/{runbook_id}/"
        if state_dir_path != expected_state_dir:
            print(f"Error: Runbook state_dir must be '{expected_state_dir}' so state keys off the runbook id; got '{state_dir_path}'.", file=sys.stderr)
            return 1
        state_dir = (runbook_path.parent / state_dir_path).resolve()
        if state_dir.exists() and any(state_dir.iterdir()):
            print(f"Error: Target state directory {state_dir} already exists and is not empty.", file=sys.stderr)
            return 1
        state_dir.mkdir(parents=True, exist_ok=True)
        seed_runbook_state(runbook_data, runbook_path, state_dir)
        print(f"Successfully initialized state directory: {state_dir}")
        return 0
    except RunbookLoadError as exc:
        print(f"init-runbook-state: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"init-runbook-state: Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
