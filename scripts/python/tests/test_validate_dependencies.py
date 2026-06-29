"""test_validate_dependencies.py — Tests for validate-dependencies CLI and lib.

Covers:
  - Lib: validate() with all graph topologies and violation types
  - CLI: Click command via CliRunner (file input, stdin, errors)

Run from ``scripts/python/``:

    uv run pytest tests/test_validate_dependencies.py -v
"""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from cli.validate_dependencies import main
from lib.validate_dependencies import validate

# ============================================================================
# Lib: validate()
# ============================================================================


class TestValidate:
    """Tests for the lib-level validate() function."""

    # -- Valid topologies ----------------------------------------------------

    def test_empty_list(self) -> None:
        valid, errors = validate([])
        assert valid is True
        assert errors == []

    def test_single_task_no_deps(self) -> None:
        tasks = [{"id": "A", "dependencies": []}]
        valid, errors = validate(tasks)
        assert valid is True
        assert errors == []

    def test_single_task_implicit_deps(self) -> None:
        """Missing 'dependencies' key is treated as empty list."""
        tasks = [{"id": "A"}]
        valid, errors = validate(tasks)
        assert valid is True
        assert errors == []

    def test_linear_chain(self) -> None:
        """A → B → C"""
        tasks = [
            {"id": "A", "dependencies": []},
            {"id": "B", "dependencies": ["A"]},
            {"id": "C", "dependencies": ["B"]},
        ]
        valid, errors = validate(tasks)
        assert valid is True
        assert errors == []

    def test_fan_out(self) -> None:
        """1 → [2, 3]"""
        tasks = [
            {"id": "1", "dependencies": []},
            {"id": "2", "dependencies": ["1"]},
            {"id": "3", "dependencies": ["1"]},
        ]
        valid, errors = validate(tasks)
        assert valid is True
        assert errors == []

    def test_fan_in(self) -> None:
        """[2, 3] → 1"""
        tasks = [
            {"id": "1", "dependencies": ["2", "3"]},
            {"id": "2", "dependencies": []},
            {"id": "3", "dependencies": []},
        ]
        valid, errors = validate(tasks)
        assert valid is True
        assert errors == []

    def test_diamond(self) -> None:
        """1 → [2, 3] → 4"""
        tasks = [
            {"id": "1", "dependencies": []},
            {"id": "2", "dependencies": ["1"]},
            {"id": "3", "dependencies": ["1"]},
            {"id": "4", "dependencies": ["2", "3"]},
        ]
        valid, errors = validate(tasks)
        assert valid is True
        assert errors == []

    def test_parallel_no_deps(self) -> None:
        """Multiple tasks, none depend on each other."""
        tasks = [
            {"id": "A", "dependencies": []},
            {"id": "B", "dependencies": []},
            {"id": "C", "dependencies": []},
        ]
        valid, errors = validate(tasks)
        assert valid is True
        assert errors == []

    # -- Violations: orphan --------------------------------------------------

    def test_orphan_dependency(self) -> None:
        tasks = [
            {"id": "A", "dependencies": ["MISSING"]},
            {"id": "B", "dependencies": []},
        ]
        valid, errors = validate(tasks)
        assert valid is False
        assert any("orphan" in e.lower() for e in errors)
        assert "MISSING" in errors[0]

    # -- Violations: self-loop -----------------------------------------------

    def test_self_loop(self) -> None:
        tasks = [{"id": "A", "dependencies": ["A"]}]
        valid, errors = validate(tasks)
        assert valid is False
        assert any("self-loop" in e.lower() for e in errors)

    # -- Violations: cycles --------------------------------------------------

    def test_direct_cycle(self) -> None:
        """1 → 2 → 1"""
        tasks = [
            {"id": "1", "dependencies": ["2"]},
            {"id": "2", "dependencies": ["1"]},
        ]
        valid, errors = validate(tasks)
        assert valid is False
        assert any("cycle" in e.lower() for e in errors)

    def test_indirect_cycle(self) -> None:
        """1 → 2 → 3 → 1"""
        tasks = [
            {"id": "1", "dependencies": ["2"]},
            {"id": "2", "dependencies": ["3"]},
            {"id": "3", "dependencies": ["1"]},
        ]
        valid, errors = validate(tasks)
        assert valid is False
        assert any("cycle" in e.lower() for e in errors)

    # -- Multi-violation -----------------------------------------------------

    def test_multiple_violations(self) -> None:
        """Self-loop + orphan + cycle in a single graph."""
        tasks = [
            {"id": "A", "dependencies": ["A"]},  # self-loop
            {"id": "B", "dependencies": ["GHOST"]},  # orphan
            {"id": "C", "dependencies": ["D"]},
            {"id": "D", "dependencies": ["C"]},  # cycle C→D→C
        ]
        valid, errors = validate(tasks)
        assert valid is False
        messages = " ".join(errors).lower()
        assert "self-loop" in messages
        assert "orphan" in messages
        assert "cycle" in messages


# ============================================================================
# CLI: validate-dependencies Click command
# ============================================================================


class TestCli:
    """Tests for the Click CLI command via CliRunner."""

    # -- Valid inputs --------------------------------------------------------

    def test_valid_graph_from_file(self, tmp_path: Path) -> None:
        path = tmp_path / "tasks.json"
        tasks = [{"id": "A", "dependencies": []}]
        path.write_text(json.dumps(tasks))
        runner = CliRunner()
        result = runner.invoke(main, [str(path)])
        assert result.exit_code == 0
        assert json.loads(result.output) == {"valid": True}

    def test_valid_graph_from_stdin(self) -> None:
        tasks = [{"id": "A", "dependencies": ["B"]}, {"id": "B", "dependencies": []}]
        runner = CliRunner()
        result = runner.invoke(main, ["--stdin"], input=json.dumps(tasks))
        assert result.exit_code == 0
        assert json.loads(result.output) == {"valid": True}

    # -- Invalid graph (violations) ------------------------------------------

    def test_cycle_graph_from_file(self, tmp_path: Path) -> None:
        path = tmp_path / "cycle.json"
        tasks = [
            {"id": "1", "dependencies": ["2"]},
            {"id": "2", "dependencies": ["1"]},
        ]
        path.write_text(json.dumps(tasks))
        runner = CliRunner()
        result = runner.invoke(main, [str(path)])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["valid"] is False
        assert len(data["errors"]) > 0

    # -- Error cases: parse / file errors ------------------------------------

    def test_non_json_input(self, tmp_path: Path) -> None:
        path = tmp_path / "bad.txt"
        path.write_text("not json")
        runner = CliRunner()
        result = runner.invoke(main, [str(path)])
        assert result.exit_code == 2
        assert "Error" in result.output

    def test_non_array_json(self, tmp_path: Path) -> None:
        path = tmp_path / "obj.json"
        path.write_text('{"id": "A"}')
        runner = CliRunner()
        result = runner.invoke(main, [str(path)])
        assert result.exit_code == 2
        assert "JSON array" in result.output

    def test_file_not_found(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["/nonexistent/path.json"])
        # Click's Path type raises BadParameter for non-existent files
        assert result.exit_code != 0

    def test_no_args_and_no_stdin(self) -> None:
        """No file path and no --stdin flag → error."""
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code == 2
        assert "Error" in result.output

    def test_help_text(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "validate-dependencies" in result.output
        assert "stdin" in result.output
