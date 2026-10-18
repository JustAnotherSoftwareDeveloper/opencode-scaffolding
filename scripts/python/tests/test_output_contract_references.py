"""Coherence checks for the canonical worker output contract."""

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

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
    """Read a repository file as text."""
    return (ROOT / relative).read_text()


def test_output_contract_declares_canonical_authority() -> None:
    """Verify the canonical output contract declares its required fields."""
    content = read(CONTRACT)
    assert "sole canonical source" in content
    for field in REQUIRED_FIELDS:
        assert f"- **{field}:**" in content


def test_active_producers_and_consumers_reference_canonical_contract() -> None:
    """Verify active agents and skills reference the canonical contract."""
    for relative in CONSUMERS:
        assert CONTRACT in read(relative), relative


def test_agents_keep_distinct_contract_read_policies() -> None:
    """Verify each agent can read the contract within its safety boundaries."""
    config = json.loads(read("opencode.json"))
    contract_path = f"~/.config/opencode/{CONTRACT}"

    delegator = config["agent"]["delegator"]["permission"]
    assert delegator["read"]["*"] == "allow"
    assert delegator["read"][contract_path] == "allow"
    assert delegator["external_directory"][contract_path] == "allow"
    for pattern in (
        "skills/**",
        ".opencode/skills/**",
        ".claude/skills/**",
        ".agents/skills/**",
        "~/.config/opencode/skills/**",
        ".env",
        ".env.*",
        "**/.env",
        "**/.env.*",
    ):
        assert delegator["read"][pattern] == "deny"

    executor = config["agent"]["executor"]["permission"]
    assert executor["read"]["*"] == "deny"
    assert executor["read"][CONTRACT] == "allow"
    assert executor["read"][f"*/{CONTRACT}"] == "allow"
    assert executor["external_directory"]["*"] == "deny"
    assert executor["external_directory"][contract_path] == "allow"


def test_structured_fixtures_use_canonical_list_grammar() -> None:
    """Verify structured worker fixtures use the canonical list grammar."""
    fixture_root = "skills/task-delegation/reference/fixtures"
    for name in STRUCTURED_FIXTURES:
        content = read(f"{fixture_root}/{name}")
        assert "| Field | Value |" not in content, name
        assert "- **Status:**" in content, name
        for field in REQUIRED_FIELDS[1:]:
            assert f"- **{field}:**" in content, f"{name}: {field}"


def test_legacy_table_is_only_an_invalid_fixture() -> None:
    """Verify only the invalid fixture uses the legacy table envelope."""
    fixture_root = ROOT / "skills/task-delegation/reference/fixtures"
    table_fixtures = {
        path.name
        for path in fixture_root.glob("*.txt")
        if "| Field | Value |" in path.read_text()
    }
    assert table_fixtures == {"invalid-table-envelope.txt"}
