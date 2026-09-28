"""The restricted executor can recover complete tasks from large plan JSON."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_executor_exposes_only_bounded_read_only_task_selection() -> None:
    config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    permissions = config["agent"]["executor"]["permission"]
    commands = permissions["bash"]
    assert commands["*"] == "deny"
    assert all("jq " not in command for command in commands)
    for path in (".plans/*/tasks.json", ".tasks/*.json"):
        prefix = f"uv run --project scripts/python get-task {path} "
        for selector in ("--id *", "--index *"):
            assert commands[prefix + selector] == "allow"
        validator = f"uv run --project scripts/python validate-task-structure {path} "
        assert (
            commands[
                validator
                + "--schema skills/breakdown-tasks/schema/task-packet.schema.json"
            ]
            == "allow"
        )
    assert permissions["task"]["worker"] == "allow"
    assert permissions["skill"]["display-tasks"] == "allow"
    assert permissions["skill"]["task-delegation"] == "allow"


def test_executor_requires_full_object_before_worker_dispatch() -> None:
    contract = (ROOT / "agents/executor.md").read_text(encoding="utf-8")
    assert "get-task PATH --index N" in contract
    assert "Never send a task ID, plan path, summary" in contract
    assert "Reconstruct the unchanged canonical root" in contract
