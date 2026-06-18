#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKSPACE_ROOT))


def main() -> int:
    from lib.collect_skills.cli import parse_args
    from lib.collect_skills.discovery import discover_all_skills
    from lib.collect_skills.models import SkillIndex

    args = parse_args()

    index = SkillIndex()

    try:
        discover_all_skills(index, args)
    except Exception as exc:
        print(f"[collect-skills] Error during discovery: {exc}", file=sys.stderr)
        return 1

    json_output = index.to_json()

    if args.output:
        try:
            args.output.write_text(json_output, encoding="utf-8")
        except OSError as exc:
            print(f"[collect-skills] Error writing output: {exc}", file=sys.stderr)
            return 1
    else:
        print(json_output)

    if args.verbose and index.warnings:
        for warning in index.warnings:
            print(f"[collect-skills] Warning: {warning}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
