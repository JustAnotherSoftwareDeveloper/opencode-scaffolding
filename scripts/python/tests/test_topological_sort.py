"""test_topological_sort.py — Tests for the topological-sort library & CLI.

Covers the lib.sort() function (via ``lib.topological_sort``) and the Click
CLI command (via CliRunner).  Tests exercise all standard graph topologies
as well as error paths (cycle detection, parse errors, missing fields).

Run from ``scripts/python/``:

    uv run pytest tests/test_topological_sort.py -v \\
        --cov=cli.topological_sort --cov=lib.topological_sort \\
        --cov-report=term-missing
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from cli.topological_sort import _read_input, main
from lib.topological_sort import sort

# ============================================================================
# Test sort() — library function
# ============================================================================


class TestSort:
    """Tests for the ``lib.topological_sort.sort()`` function."""

    # -- Happy path: graph topologies ---------------------------------------

    def test_empty_list(self) -> None:
        """An empty task list produces an empty result."""
        assert sort([]) == []

    def test_single_task(self) -> None:
        """A single task with no dependencies is returned as-is."""
        tasks = [{"id": "a"}]
        assert sort(tasks) == [{"id": "a"}]

    def test_single_task_with_empty_deps(self) -> None:
        """A single task with an empty dependency list."""
        tasks = [{"id": "a", "dependencies": []}]
        assert sort(tasks) == [{"id": "a", "dependencies": []}]

    def test_linear_chain(self) -> None:
        """Linear chain A -> B -> C."""
        tasks = [
            {"id": "c", "dependencies": ["b"]},
            {"id": "b", "dependencies": ["a"]},
            {"id": "a", "dependencies": []},
        ]
        result = sort(tasks)
        ids = [t["id"] for t in result]
        # a must come before b, b before c
        assert ids.index("a") < ids.index("b") < ids.index("c")

    def test_fan_out(self) -> None:
        """Fan-out: A -> [B, C, D]."""
        tasks = [
            {"id": "a", "dependencies": []},
            {"id": "b", "dependencies": ["a"]},
            {"id": "c", "dependencies": ["a"]},
            {"id": "d", "dependencies": ["a"]},
        ]
        result = sort(tasks)
        ids = [t["id"] for t in result]
        # a must come first
        assert ids[0] == "a"
        # b, c, d must be sorted lexicographically
        assert ids[1:] == ["b", "c", "d"]

    def test_fan_in(self) -> None:
        """Fan-in: [A, B] -> C."""
        tasks = [
            {"id": "c", "dependencies": ["a", "b"]},
            {"id": "b", "dependencies": []},
            {"id": "a", "dependencies": []},
        ]
        result = sort(tasks)
        ids = [t["id"] for t in result]
        # a and b must both come before c
        assert ids.index("a") < ids.index("c")
        assert ids.index("b") < ids.index("c")

    def test_diamond(self) -> None:
        """Diamond: A -> B, A -> C, B -> D, C -> D."""
        tasks = [
            {"id": "a", "dependencies": []},
            {"id": "d", "dependencies": ["b", "c"]},
            {"id": "c", "dependencies": ["a"]},
            {"id": "b", "dependencies": ["a"]},
        ]
        result = sort(tasks)
        ids = [t["id"] for t in result]
        assert ids.index("a") < ids.index("b")
        assert ids.index("a") < ids.index("c")
        assert ids.index("b") < ids.index("d")
        assert ids.index("c") < ids.index("d")

    def test_parallel_tasks_deterministic(self) -> None:
        """Parallel tasks with same depth are sorted lexicographically by id.

        Three independent tasks should appear in alphabetical order.
        """
        tasks = [
            {"id": "z", "dependencies": []},
            {"id": "c", "dependencies": []},
            {"id": "m", "dependencies": []},
        ]
        result = sort(tasks)
        ids = [t["id"] for t in result]
        assert ids == ["c", "m", "z"]

    def test_deep_diamond_with_parallel_sorting(self) -> None:
        """Mixed depth: ensure deterministic sort across levels.

        Kahn's algorithm with sorted ready queue processes 'a' at level 0
        (smallest id), which makes 'b' ready. The ready queue becomes
        ['b', 'c'] (sorted), so 'b' is dequeued before 'c'.
        """
        tasks = [
            {"id": "b", "dependencies": ["a"]},
            {"id": "d", "dependencies": ["c"]},
            {"id": "a", "dependencies": []},
            {"id": "c", "dependencies": []},
        ]
        result = sort(tasks)
        ids = [t["id"] for t in result]
        assert ids == ["a", "b", "c", "d"]

    def test_preserves_extra_fields(self) -> None:
        """Fields besides id/dependencies are preserved in the output."""
        tasks = [
            {"id": "b", "dependencies": ["a"], "value": 42},
            {"id": "a", "dependencies": [], "name": "first"},
        ]
        result = sort(tasks)
        assert result[0] == {"id": "a", "dependencies": [], "name": "first"}
        assert result[1] == {"id": "b", "dependencies": ["a"], "value": 42}

    # -- Error paths --------------------------------------------------------

    def test_cycle_simple(self) -> None:
        """A -> B -> A raises ValueError with cycle path."""
        tasks = [
            {"id": "a", "dependencies": ["b"]},
            {"id": "b", "dependencies": ["a"]},
        ]
        with pytest.raises(ValueError, match="Cycle detected: a -> b -> a"):
            sort(tasks)

    def test_cycle_longer(self) -> None:
        """A -> B -> C -> A raises ValueError."""
        tasks = [
            {"id": "a", "dependencies": ["c"]},
            {"id": "b", "dependencies": ["a"]},
            {"id": "c", "dependencies": ["b"]},
        ]
        with pytest.raises(ValueError, match="Cycle detected"):
            sort(tasks)

    def test_cycle_self_loop(self) -> None:
        """A -> A (self-loop) raises ValueError."""
        tasks = [
            {"id": "a", "dependencies": ["a"]},
        ]
        with pytest.raises(ValueError, match="Cycle detected: a -> a"):
            sort(tasks)

    def test_missing_id(self) -> None:
        """A task without an 'id' field raises ValueError."""
        tasks = [{"dependencies": []}]
        with pytest.raises(ValueError, match="missing or invalid 'id' field"):
            sort(tasks)

    def test_invalid_id_type(self) -> None:
        """A task with a non-string 'id' raises ValueError."""
        tasks = [{"id": 123}]
        with pytest.raises(ValueError, match="missing or invalid 'id' field"):
            sort(tasks)

    def test_duplicate_id(self) -> None:
        """Duplicate task ids raise ValueError."""
        tasks = [{"id": "a"}, {"id": "a"}]
        with pytest.raises(ValueError, match="Duplicate task id: a"):
            sort(tasks)

    def test_invalid_dependencies_type(self) -> None:
        """Non-list 'dependencies' field raises ValueError."""
        tasks = [{"id": "a", "dependencies": "not-a-list"}]
        with pytest.raises(ValueError, match="invalid 'dependencies' field"):
            sort(tasks)

    def test_non_string_dependency(self) -> None:
        """A dependency that is not a string raises ValueError."""
        tasks = [{"id": "a", "dependencies": [42]}]
        with pytest.raises(ValueError, match="non-string dependency"):
            sort(tasks)

    def test_unknown_dependency(self) -> None:
        """A dependency referencing a non-existent task raises ValueError."""
        tasks = [{"id": "a", "dependencies": ["b"]}]
        with pytest.raises(ValueError, match="depends on unknown task 'b'"):
            sort(tasks)


# ============================================================================
# Test internal helpers
# ============================================================================


class TestReadInput:
    """Tests for the internal ``_read_input`` function."""

    def test_nonexistent_file(self) -> None:
        """A non-existent file path raises ValueError wrapped OSError."""
        with pytest.raises(ValueError, match="Cannot read file"):
            _read_input("/tmp/nonexistent_file_for_test.json")


# ============================================================================
# Test Click CLI via CliRunner
# ============================================================================


class TestCli:
    """Tests for the Click CLI command via CliRunner."""

    # -- Help text ----------------------------------------------------------

    def test_help_text(self) -> None:
        """--help prints usage information."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "topological-sort" in result.output

    # -- Stdin mode ---------------------------------------------------------

    def test_empty_list_stdin(self) -> None:
        """Empty list via stdin produces []."""
        runner = CliRunner()
        result = runner.invoke(main, ["--stdin"], input="[]")
        assert result.exit_code == 0
        assert result.output.strip() == "[]"

    def test_single_task_stdin(self) -> None:
        """Single task via stdin."""
        tasks = [{"id": "a"}]
        runner = CliRunner()
        result = runner.invoke(main, ["--stdin"], input=json.dumps(tasks))
        assert result.exit_code == 0
        assert json.loads(result.output) == tasks

    def test_linear_chain_stdin(self) -> None:
        """Linear chain A -> B -> C via stdin."""
        tasks = [
            {"id": "c", "dependencies": ["b"]},
            {"id": "b", "dependencies": ["a"]},
            {"id": "a", "dependencies": []},
        ]
        runner = CliRunner()
        result = runner.invoke(main, ["--stdin"], input=json.dumps(tasks))
        assert result.exit_code == 0
        sorted_ids = [t["id"] for t in json.loads(result.output)]
        assert sorted_ids == ["a", "b", "c"]

    def test_fan_out_stdin(self) -> None:
        """Fan-out via stdin — parallel tasks sorted by id."""
        tasks = [
            {"id": "a", "dependencies": []},
            {"id": "c", "dependencies": ["a"]},
            {"id": "b", "dependencies": ["a"]},
        ]
        runner = CliRunner()
        result = runner.invoke(main, ["--stdin"], input=json.dumps(tasks))
        assert result.exit_code == 0
        sorted_ids = [t["id"] for t in json.loads(result.output)]
        assert sorted_ids == ["a", "b", "c"]

    def test_diamond_stdin(self) -> None:
        """Diamond topology via stdin."""
        tasks = [
            {"id": "d", "dependencies": ["b", "c"]},
            {"id": "b", "dependencies": ["a"]},
            {"id": "c", "dependencies": ["a"]},
            {"id": "a", "dependencies": []},
        ]
        runner = CliRunner()
        result = runner.invoke(main, ["--stdin"], input=json.dumps(tasks))
        assert result.exit_code == 0
        sorted_ids = [t["id"] for t in json.loads(result.output)]
        assert sorted_ids == ["a", "b", "c", "d"]

    # -- File input mode ----------------------------------------------------

    def test_file_input(self, tmp_path: Path) -> None:
        """Reading from a file path succeeds."""
        tasks = [{"id": "a"}, {"id": "b", "dependencies": ["a"]}]
        data_file = tmp_path / "tasks.json"
        data_file.write_text(json.dumps(tasks))
        runner = CliRunner()
        result = runner.invoke(main, [str(data_file)])
        assert result.exit_code == 0
        sorted_ids = [t["id"] for t in json.loads(result.output)]
        assert sorted_ids == ["a", "b"]

    # -- Error paths --------------------------------------------------------

    def test_no_file_no_stdin(self) -> None:
        """No arguments produces exit code 2."""
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code == 2
        assert "Provide a file path" in result.output

    def test_invalid_json(self) -> None:
        """Non-JSON input produces exit code 2."""
        runner = CliRunner()
        result = runner.invoke(main, ["--stdin"], input="not json")
        assert result.exit_code == 2
        assert "Error:" in result.output

    def test_non_array_json(self) -> None:
        """JSON that is not an array produces exit code 2."""
        runner = CliRunner()
        result = runner.invoke(main, ["--stdin"], input='"hello"')
        assert result.exit_code == 2
        assert "Input must be a JSON array" in result.output

    def test_missing_id_via_cli(self) -> None:
        """Task missing id field — sort() raises ValueError, CLI exits code 1."""
        runner = CliRunner()
        result = runner.invoke(main, ["--stdin"], input='[{"dependencies": []}]')
        assert result.exit_code == 1
        assert "Error:" in result.output

    def test_cycle_via_cli(self) -> None:
        """Cycle detection: exit code 1, original input on stdout, cycle on stderr."""
        tasks = [
            {"id": "a", "dependencies": ["b"]},
            {"id": "b", "dependencies": ["a"]},
        ]
        runner = CliRunner()
        result = runner.invoke(main, ["--stdin"], input=json.dumps(tasks))
        assert result.exit_code == 1
        # stdout must contain the original input JSON
        assert json.loads(result.stdout) == tasks
        # stderr must contain the cycle path
        assert "Cycle detected: a -> b -> a" in result.stderr

    def test_unknown_dependency_via_cli(self) -> None:
        """Unknown dependency — sort() raises ValueError, CLI exits code 1."""
        runner = CliRunner()
        result = runner.invoke(
            main, ["--stdin"], input='[{"id": "a", "dependencies": ["b"]}]'
        )
        assert result.exit_code == 1
        assert "Error:" in result.output
