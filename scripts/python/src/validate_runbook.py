#!/usr/bin/env python3
"""CLI command to validate runbooks in v1 JSON or v2 XML format.

Usage:
    validate-runbook <runbook_path> [--strict]
    
Examples:
    # Validate a v2 XML runbook
    validate-runbook .runbooks/my-runbook/main.xml
    
    # Validate a legacy v1 JSON runbook  
    validate-runbook .runbooks/my-runbook/runbook.json
    
    # Validate with strict mode (unreferenced steps are errors)
    validate-runbook .runbooks/my-runbook/main.xml --strict
    
    # Output as JSON
    validate-runbook .runbooks/my-runbook/main.xml --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from lib.runbook_xml import validate_runbook, RunbookLoadError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a runbook in v1 JSON or v2 XML format."
    )
    parser.add_argument(
        "runbook_path",
        help="Path to runbook.json (v1) or main.xml (v2)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (e.g., unreferenced step files)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    
    runbook_path = Path(args.runbook_path)
    
    try:
        is_valid, messages = validate_runbook(runbook_path, strict=args.strict)
        
        if args.json:
            # Output as minimal JSON
            result = {
                "valid": is_valid,
                "messages": messages
            }
            print(json.dumps(result))
        else:
            # Output as text
            for msg in messages:
                print(msg)
            
            if is_valid:
                print("\n✓ Runbook is valid")
                return 0
            else:
                print("\n✗ Runbook validation failed")
                return 1
                
    except RunbookLoadError as e:
        if args.json:
            result = {
                "valid": False,
                "messages": [f"Error: {e}"]
            }
            if e.details:
                result["details"] = e.details
            print(json.dumps(result))
        else:
            print(f"Error: {e}", file=sys.stderr)
            if e.details:
                for key, value in e.details.items():
                    print(f"  {key}: {value}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        if args.json:
            result = {
                "valid": False,
                "messages": [f"Error: File not found: {runbook_path}"]
            }
            print(json.dumps(result))
        else:
            print(f"Error: File not found: {runbook_path}", file=sys.stderr)
        return 1
    except Exception as e:
        if args.json:
            result = {
                "valid": False,
                "messages": [f"Unexpected error: {e}"]
            }
            print(json.dumps(result))
        else:
            print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
