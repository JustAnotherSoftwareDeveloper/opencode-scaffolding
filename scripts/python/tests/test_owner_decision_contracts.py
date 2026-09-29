"""Source-level checks for the approved clarification and recovery boundaries."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_no_material_question_blocks_without_empty_tool_call() -> None:
    content = (ROOT / "skills/ask-question/SKILL.md").read_text(encoding="utf-8")
    schemas = [
        json.loads(block)
        for block in re.findall(r"```json\n(.*?)\n```", content, re.DOTALL)
    ]
    assert schemas[0]["properties"]["questions"]["minItems"] == 1
    assert schemas[1]["properties"]["answers"].get("minItems") is None
    assert (
        "BLOCKED: No unanswered question would materially change the next step."
        in content
    )
    assert (
        "Do not invoke the question tool or return an empty-answer completion."
        in content
    )
    assert "Do not invent confirmation or preference questions" in content


def test_malformed_report_requires_supervisory_redispatch_not_repair() -> None:
    delegation = (ROOT / "skills/task-delegation/SKILL.md").read_text(encoding="utf-8")
    delegator = (ROOT / "agents/delegator.md").read_text(encoding="utf-8")
    executor = (ROOT / "agents/executor.md").read_text(encoding="utf-8")
    for content in (delegation, delegator, executor):
        assert "original response" in content
        assert "diagnostics" in content
        assert "re-dispatch" in content
    assert "Never translate malformed output into a valid report" in delegation
    assert "one worker per\ninvocation" in delegation
    assert "transient" in delegator
    assert re.search(r"does not repair\s+the approved packet", executor)
