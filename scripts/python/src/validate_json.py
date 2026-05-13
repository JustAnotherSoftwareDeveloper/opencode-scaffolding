from __future__ import annotations

import argparse
import sys

from lib.json_validation import JsonValidationError, validate_json_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate JSON syntax and optional JSON Schema conformance.")
    parser.add_argument("json_file", help="Path to the JSON file to validate.")
    parser.add_argument("--schema", help="Optional path to a JSON Schema file.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        validate_json_path(args.json_file, args.schema)
    except JsonValidationError as exc:
        print(f"validate-json: {exc}", file=sys.stderr)
        return 1

    print(f"validate-json: valid: {args.json_file}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
