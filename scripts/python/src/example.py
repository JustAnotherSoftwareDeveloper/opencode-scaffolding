#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKSPACE_ROOT))

from lib.example import example_message


def main() -> int:
    print(example_message("python"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
