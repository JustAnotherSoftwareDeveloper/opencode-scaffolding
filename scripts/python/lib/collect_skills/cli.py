"""CLI argument parsing for collect-skills."""

from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    """Build and return the configured argument parser."""
    parser = argparse.ArgumentParser(description="Collect OpenCode skills")

    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: current working directory)",
    )

    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path.home() / ".config" / "opencode",
        help="Global configuration directory (default: ~/.config/opencode)",
    )

    parser.add_argument(
        "--extra-paths",
        type=Path,
        nargs="*",
        default=[],
        help="Additional scan directories",
    )

    parser.add_argument(
        "--include-archive",
        action="store_true",
        default=False,
        help="Include archive/ directories in skill discovery",
    )

    parser.add_argument(
        "--builtins-manifest",
        type=Path,
        default=None,
        help="JSON file listing built-in skills",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Print warnings and progress to stderr",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Write JSON output to file instead of stdout",
    )

    return parser


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments.

    Accepts an optional list of strings for testability.
    When ``None``, ``sys.argv`` is used.
    """
    return build_parser().parse_args(args)
