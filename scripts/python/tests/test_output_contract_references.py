"""Coherence checks for the canonical worker output contract."""

import json
from pathlib import Path


ROOT = Path(__file__).parents[3]
CONTRACT = "output-contract-template.md"

CONSUMERS = (
    "agents/worker.md",
    "agents/delegator.md",
    "agents/executor.md",
    "skills/task-delegation/SKILL.md",
    "skills/dispatch-decompose/SKILL.md",
    "skills/customize-opencode/SKILL.md",
    "skills/skill-template-library/templates/delegated.SKILL.template.md",
    "skills/task-delegation/reference/README.md",
)

STRUCTURED_FIXTURES = (
    "blocked.txt",
    "complete-file-change.txt",
    "complete-markdown-payload.txt",
    "complete-no-files.txt",
    "decomposition-complete.txt",
    "empty-success-payload.txt",
    "false-completion.txt",
    "list-multiline-payload.txt",
    "malformed-status.txt",
    "partial.txt",
)

REQUIRED_FIELDS = (
    "Status",
    "What was done",
    "Accomplishments",
    "Files modified",
    "Skills loaded",
    "Planning context loaded",
    "Reads relied on",
    "Deviations",
    "Blocker",
    "Unblock condition",
)


def read(relative: str) -> str:
    return (ROOT / relative).read_text()


def test_output_contract_declares_canonical_authority() -> None:
    content = read(CONTRACT)
    assert "sole canonical source" in content
    for field in REQUIRED_FIELDS:
        assert f"- **{field}:**" in content


def test_active_producers_and_consumers_reference_canonical_contract() -> None:
    for relative in CONSUMERS:
        assert CONTRACT in read(relative), relative


def test_restricted_agents_can_read_canonical_contract() -> None:
    config = json.loads(read("opencode.json"))
    for name in ("delegator", "executor"):
        permissions = config["agent"][name]["permission"]["read"]
        assert permissions[CONTRACT] == "allow"


def test_structured_fixtures_use_canonical_list_grammar() -> None:
    fixture_root = "skills/task-delegation/reference/fixtures"
    for name in STRUCTURED_FIXTURES:
        content = read(f"{fixture_root}/{name}")
        assert "| Field | Value |" not in content, name
        assert "- **Status:**" in content, name
        for field in REQUIRED_FIELDS[1:]:
            assert f"- **{field}:**" in content, f"{name}: {field}"


def test_legacy_table_is_only_an_invalid_fixture() -> None:
    fixture_root = ROOT / "skills/task-delegation/reference/fixtures"
    table_fixtures = {
        path.name
        for path in fixture_root.glob("*.txt")
        if "| Field | Value |" in path.read_text()
    }
    assert table_fixtures == {"invalid-table-envelope.txt"}
