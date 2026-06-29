"""test_generate_uuids.py — Tests for generate-uuids CLI and lib modules.

Covers the ``lib.generate_uuids.generate()`` function directly (unit tests)
and the Click CLI command via CliRunner (integration tests).

Run from ``scripts/python/``:

    uv run pytest tests/test_generate_uuids.py -v \\
        --cov=cli.generate_uuids --cov=lib.generate_uuids \\
        --cov-report=term-missing
"""

from __future__ import annotations

import json
import re
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from cli.generate_uuids import main
from lib.generate_uuids import generate

# Regex for a valid UUID v4 string.
# Format: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx where y is [89ab].
_UUID_V4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


# ============================================================================
# Unit tests — lib.generate_uuids.generate()
# ============================================================================


class TestGenerateUuidsLib:
    """Direct unit tests for the ``generate()`` library function."""

    # -- Nominal cases -------------------------------------------------------

    @pytest.mark.parametrize("count", [1, 5, 100])
    def test_generate_valid_counts(self, count: int) -> None:
        """Valid counts return the correct number of UUIDs."""
        uuids = generate(count)
        assert len(uuids) == count

    @pytest.mark.parametrize("count", [1, 5, 100])
    def test_generate_uuid_format(self, count: int) -> None:
        """Every generated UUID matches the v4 format pattern."""
        uuids = generate(count)
        for uid in uuids:
            assert _UUID_V4_RE.match(uid), f"Invalid UUID v4 format: {uid}"

    @pytest.mark.parametrize("count", [1, 5, 100])
    def test_generate_uniqueness(self, count: int) -> None:
        """All UUIDs generated in a single call are unique."""
        uuids = generate(count)
        assert len(set(uuids)) == count

    # -- Error cases ---------------------------------------------------------

    @pytest.mark.parametrize(
        "count, expected_msg",
        [
            (0, "count must be between 1 and 100, got 0"),
            (101, "count must be between 1 and 100, got 101"),
            (-1, "count must be between 1 and 100, got -1"),
        ],
    )
    def test_generate_invalid_counts(self, count: int, expected_msg: str) -> None:
        """Counts outside [1, 100] raise ValueError."""
        with pytest.raises(ValueError, match=re.escape(expected_msg)):
            generate(count)


# ============================================================================
# CLI integration tests — cli.generate_uuids.main via CliRunner
# ============================================================================


class TestGenerateUuidsCli:
    """Integration tests for the Click CLI via CliRunner."""

    # -- Nominal cases -------------------------------------------------------

    @pytest.mark.parametrize("count", ["1", "5", "100"])
    def test_cli_valid_counts(self, runner: CliRunner, count: str) -> None:
        """Valid counts exit 0 and produce a JSON array of UUIDs."""
        result = runner.invoke(main, [count])
        assert result.exit_code == 0, f"STDERR: {result.output}"
        uuids = json.loads(result.output)
        assert isinstance(uuids, list)
        assert len(uuids) == int(count)

    @pytest.mark.parametrize("count", ["1", "5", "100"])
    def test_cli_uuid_format(self, runner: CliRunner, count: str) -> None:
        """CLI output UUIDs match the v4 format pattern."""
        result = runner.invoke(main, [count])
        assert result.exit_code == 0
        uuids = json.loads(result.output)
        for uid in uuids:
            assert _UUID_V4_RE.match(uid), f"Invalid UUID v4 format: {uid}"

    @pytest.mark.parametrize("count", ["1", "5", "100"])
    def test_cli_uniqueness(self, runner: CliRunner, count: str) -> None:
        """CLI-generated UUIDs in a single call are unique."""
        result = runner.invoke(main, [count])
        assert result.exit_code == 0
        uuids = json.loads(result.output)
        assert len(set(uuids)) == int(count)

    # -- Error cases: bounds and invalid input --------------------------------

    @pytest.mark.parametrize(
        "count, expected_exit_code, expected_substring",
        [
            ("0", 2, "Error:"),
            ("101", 2, "Error:"),
            ("-1", 2, "No such option"),
        ],
    )
    def test_cli_invalid_counts(
        self,
        runner: CliRunner,
        count: str,
        expected_exit_code: int,
        expected_substring: str,
    ) -> None:
        """Counts outside [1, 100] exit 1; negative parsed as unknown option exits 2."""
        result = runner.invoke(main, [count])
        assert result.exit_code == expected_exit_code
        assert expected_substring in result.output

    # -- Error case: unexpected exception in lib ------------------------------

    def test_cli_lib_unexpected_error(self, runner: CliRunner) -> None:
        """An unexpected exception in the lib module exits 1."""
        with patch("cli.generate_uuids.generate", side_effect=RuntimeError("boom")):
            result = runner.invoke(main, ["5"])
        assert result.exit_code == 1
        assert "Error: boom" in result.stderr

    # -- Help flag -----------------------------------------------------------

    def test_cli_help(self, runner: CliRunner) -> None:
        """--help displays usage information and exits 0."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "generate-uuids" in result.output
        assert "COUNT" in result.output
