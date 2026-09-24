"""Regression checks for the intended top-level agent role boundaries."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AGENTS = ROOT / "agents"


def _text(name: str) -> str:
    return (AGENTS / name).read_text(encoding="utf-8")


def test_delegator_is_smart_read_only_supervisor() -> None:
    text = _text("delegator.md")

    assert "detect obviously wrong tasks" in text
    assert "Structural validity is not evidence that a task is semantically sane" in text
    assert "Do not patch a published packet in place" in text
    assert "The accepted canonical packet remains immutable" in text
    assert "Do not silently substitute or add a second operation owner" in text
    assert "ADAPT` is a supervisory behavior, not a worker status" in text
    assert "Never use shell, edit, implementation, or research tools" in text


def test_executor_is_approved_plan_runner_subset() -> None:
    text = _text("executor.md")

    assert "execution-only subset of `delegator`" in text
    assert "task-packet.schema.json" in text
    assert "inspect its declared `dependencies`" in text
    assert "A failure in one branch does not automatically stop an independent branch" in text
    assert "Do not inspect ordinary repository files to second-guess the plan" in text
    assert "Do not merge, split, rewrite, reassign, or" in text


def test_executor_simple_runs_approved_tasks_inline() -> None:
    text = _text("executor-simple.md")

    assert "inline counterpart to `executor`" in text
    assert "inspect its declared `dependencies`" in text
    assert "load `task-executor`" in text
    assert "Do not invoke the `task` tool" in text
    assert "All actual task work occurs inline through `task-executor`" in text


def test_planner_is_direct_multi_skill_agent() -> None:
    text = _text("planner.md")

    assert "normal direct primary agent for planning work" in text
    assert "may load and use multiple applicable skills" in text
    assert "exactly one operation owner" in text
    assert "does not limit" in text
    assert "Do not use the `task` tool" in text


def test_skill_manager_is_direct_multi_skill_agent() -> None:
    text = _text("skill-manager.md")

    assert "normal direct primary agent for OpenCode skill work" in text
    assert "Load and use as many materially relevant skills" in text
    assert "exactly one operation owner" in text
    assert "does not limit this agent's whole turn" in text
    assert "Do not use the `task` tool" in text


def test_godmode_is_intentionally_unrestricted() -> None:
    text = _text("godmode.md")

    assert "unrestricted general-purpose primary agent" in text
    assert "Any number of planning, operation, documentation" in text
    assert "does not limit GodMode's own" in text
    assert "Use all available tools as needed" in text
    assert "Delegate when specialization" in text


def test_inline_task_executor_accepts_current_task_packet_and_skill_shape() -> None:
    text = (ROOT / "skills" / "task-executor" / "SKILL.md").read_text(encoding="utf-8")

    assert "conforming to the `TaskPacket` definition" in text
    assert "exactly one `class: operation` owner" in text
    assert "zero to two `class: documentation` skills" in text
    assert "Documentation skills are passive context" in text
    assert "must not reconstruct collector metadata" in text


def test_executor_config_can_validate_canonical_packet() -> None:
    config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    executor = config["agent"]["executor"]
    delegator = config["agent"]["delegator"]

    assert (
        executor["permission"]["read"]["skills/breakdown-tasks/schema/task-packet.schema.json"]
        == "allow"
    )
    assert delegator["model"] == "openai/gpt-6-sol"
    assert delegator["variant"] == "high"
    assert delegator["permission"]["glob"] == "allow"
