"""Reject local research provenance in the final Node-family skill documents."""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

ROOT = Path(__file__).resolve().parents[3]
FAMILY = (
    "node-project-writer",
    "node-project-test-writer",
    "node-project-dependencies",
    "node-quality-workflow",
    "node-package-distribution",
    "node-project-reference",
    "node-domain-planning",
    "node-source-style-guide",
)

# Match local paths and provenance labels; allow skill links and publisher URLs.
RESEARCH_REFERENCE = re.compile(
    r"(?:"
    r"(?:\.research|\.plans/(?:[^\s/)]+/)*research)(?:/|(?=[\s)#]))"
    r"|\bresearch[- ](?:artifact|bundle|record)s?\b"
    r"|\b(?:according to|based on|as shown in|from)\s+(?:the\s+)?research\b"
    r"|\b(?:claim|dossier)\s+C\d+\b"
    r"|\b\d{8}-node-ts-[a-z0-9-]+\b"
    r")",
    re.IGNORECASE,
)


def _research_references(
    documents: Iterable[tuple[str, str]],
) -> list[str]:
    """Return locations containing a local research path or provenance."""
    findings: list[str] = []
    for location, text in documents:
        match = RESEARCH_REFERENCE.search(text)
        if match:
            findings.append(f"{location}: {match.group(0)}")
    return findings


@pytest.mark.parametrize(
    "text",
    [
        "[source](../../.research/runtime/README.md)",
        "Evidence path: `.research/runtime/answer.md`",
        "See .plans/123/research/claims.md for provenance.",
        "This research bundle informed the recommendation.",
        "According to the research, this is supported.",
        "The conclusion follows claim C12.",
        "Source: 20261107-node-ts-runtime-compatibility",
    ],
)
def test_research_artifact_paths_and_provenance_are_rejected(text: str) -> None:
    """Reject path, Markdown-link, bundle, and claim-only provenance forms."""
    assert _research_references([("sample.md", text)])


def test_final_skill_internal_and_external_links_are_allowed() -> None:
    """Do not flag normal final-skill references or external source URLs."""
    text = (
        "[Focused guide](reference/guide.md)\n"
        "[Publisher docs](https://www.typescriptlang.org/docs/)\n"
    )
    assert _research_references([("sample.md", text)]) == []


def test_every_final_node_family_markdown_document_has_no_research_reference(
) -> None:
    """Scan every entrypoint and progressive disclosure, including new files."""
    assert len(FAMILY) == 8

    documents: list[tuple[str, str]] = []
    for skill in FAMILY:
        workspace = ROOT / "skills" / skill
        assert (workspace / "SKILL.md").is_file(), (
            f"missing final skill entrypoint: {workspace / 'SKILL.md'}"
        )
        documents.extend(
            (
                path.relative_to(ROOT).as_posix(),
                path.read_text(encoding="utf-8"),
            )
            for path in sorted(workspace.rglob("*.md"))
        )

    assert documents
    assert _research_references(documents) == []
