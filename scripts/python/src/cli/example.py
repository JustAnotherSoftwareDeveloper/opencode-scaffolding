#!/usr/bin/env python3
from __future__ import annotations

from lib.shared._path_helper import setup_package_path

setup_package_path()


def main() -> int:
    from lib.example import example_message

    print(example_message("python"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
