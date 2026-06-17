from __future__ import annotations

import argparse
import sys

from lib.yaml_validation import YamlValidationError, validate_yaml_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate YAML syntax.")
    parser.add_argument("yaml_file", help="Path to the YAML file to validate.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        validate_yaml_path(args.yaml_file)
    except YamlValidationError as exc:
        print(f"validate-yaml: {exc}", file=sys.stderr)
        return 1

    print(f"validate-yaml: valid: {args.yaml_file}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
