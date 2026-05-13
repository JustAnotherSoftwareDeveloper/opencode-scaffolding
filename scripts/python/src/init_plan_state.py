from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from lib.json_validation import JsonValidationError, validate_json_path
from lib.plan_state import HARNESS_ROOT, seed_plan_state



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Initialize a plan's state directory from a JSON plan file.")
    parser.add_argument("plan_file", help="Path to the JSON plan file to validate and seed state from.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        # Validate the plan file against the plan schema
        plan_path = Path(args.plan_file).resolve()
        plan_schema_path = HARNESS_ROOT / "skills/plan/schema.json"
        validate_json_path(plan_path, plan_schema_path)
        
        # Load the plan to get state_dir
        with plan_path.open("r", encoding="utf-8") as f:
            plan_data = json.load(f)

        if plan_path.parent.name != ".plans":
            print(
                f"Error: Plan file {plan_path} must be located in a .plans directory so relative state_dir paths resolve safely.",
                file=sys.stderr,
            )
            return 1
        
        # Get the state directory from the plan
        state_dir_path = plan_data.get("state_dir")
        if not state_dir_path:
            print(f"Error: Plan file {args.plan_file} does not contain a 'state_dir' field.", file=sys.stderr)
            return 1
            
        # Resolve the state directory relative to the plan file
        state_dir = plan_path.parent / state_dir_path
        state_dir = state_dir.resolve()
        
        # Check if the directory is empty or absent
        if state_dir.exists() and any(state_dir.iterdir()):
            print(f"Error: Target state directory {state_dir} already exists and is not empty.", file=sys.stderr)
            return 1
            
        # Create the state directory if it doesn't exist
        state_dir.mkdir(parents=True, exist_ok=True)
        
        # Seed the state directory
        seed_plan_state(plan_data, plan_path, state_dir)
        
        print(f"Successfully initialized state directory: {state_dir}")
        return 0
        
    except JsonValidationError as exc:
        print(f"init-plan-state: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"init-plan-state: Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
