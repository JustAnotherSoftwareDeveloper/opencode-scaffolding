"""Tests for the generate-task-json library."""

# Structured fixtures intentionally keep routing records readable.
# ruff: noqa: E501

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from lib.collect_skills.models import Skill
from lib.generate_task_json import core
from lib.generate_task_json.ranker import RankingDiagnostics, RankingResult
from lib.generate_task_json.ranking_diagnostics import AtomicDiagnosticSink
from lib.shared.skill_routing import RoutingCue, RoutingRelationship

VALID_CONTEXT = (
    "Add focused Python tests for the example CLI behavior and preserve the existing "
    "test layout. Cover the supported input path, error handling, and output contract "
    "without changing unrelated production code or adding dependencies."
)

STRUCTURED_INDEX = {
    "description": "Use when writing Python tests",
    "schema_version": "1.0",
    "cues": [{"facet": "operation", "value": "write-tests", "primary": True}],
    "relationships": [{"role": "owner"}],
}


def _drafts() -> dict:
    return {
        "summary": "Generate test task packets.",
        "tasks": [
            {
                "purpose": "Write Python tests.",
                "context": VALID_CONTEXT,
                "filesToRead": ["scripts/python/src/cli/example.py"],
                "filesToWrite": ["scripts/python/tests/test_example.py"],
                "executionInstructions": [{"step": 1, "action": "Write tests."}],
                "expectedOutput": "Python tests.",
            }
        ],
    }


def _skill(name: str = "python-test", class_: str = "operation") -> Skill:
    return Skill(
        name=name,
        description="Write Python tests",
        cues=(
            RoutingCue("operation", "write-tests", primary=True),
            RoutingCue("subject", "python"),
        ),
        relationships=(RoutingRelationship("owner"),),
        class_=class_,
    )


def _ranked_index(
    tmp_path: Path, names: tuple[str, ...] = ("python-test",)
) -> list[dict]:
    records = []
    for name in names:
        path = tmp_path / name / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("---\nname: skill\n---\n", encoding="utf-8")
        records.append(
            {
                "name": name,
                "description": f"Description for {name}",
                "schema_version": "1.0",
                "cues": [
                    {"facet": "operation", "value": "write-tests", "primary": True},
                    {"facet": "subject", "value": "python"},
                ],
                "relationships": [{"role": "owner"}],
                "class": "operation",
                "source": "project",
                "path": str(path),
            }
        )
    return records


class FakeRanker:
    def __init__(self, names: tuple[str, ...]) -> None:
        self.names = names
        self.calls = []

    def rank(self, task, candidates):
        self.calls.append((task, candidates))
        return RankingResult(
            self.names,
            RankingDiagnostics(
                tuple((candidate.name, 0.9) for candidate in candidates),
                self.names,
                False,
            ),
        )

    def diagnostic_identity(self):
        return {
            "model": "model-digest",
            "runtime": "0.31.1",
            "tokenizer": "tokenizer-digest",
            "prompt": "prompt-v1",
            "render": "render-v1",
            "policy": "policy-v1",
        }


def test_generate_task_json_writes_assigned_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(core.time, "time_ns", lambda: 1_700_000_000_123_000_000)
    output = core.generate_task_json(
        _drafts(),
        "generate-tests",
        project_root=tmp_path,
        skills_index=[
            {
                "name": "python-test",
                "description": "Write Python tests",
                "schema_version": "1.0",
                "cues": [
                    {"facet": "operation", "value": "write-tests", "primary": True},
                    {"facet": "subject", "value": "python"},
                ],
                "relationships": [{"role": "owner"}],
                "class": "operation",
            }
        ],
    )
    result = json.loads(output.read_text())
    assert output == tmp_path / ".tasks" / "1700000000123-generate-tests.json"
    assert result["tasks"][0]["skills"] == ["python-test"]


def test_qwen_ranker_is_authoritative_and_preserves_task_fields(tmp_path: Path) -> None:
    ranker = FakeRanker(("python-test",))
    drafts = _drafts()
    output = core.generate_task_json(
        drafts,
        "ranked",
        project_root=tmp_path,
        skills_index=_ranked_index(tmp_path),
        ranker=ranker,
        assignment_mode="qwen",
    )
    result = json.loads(output.read_text())
    assert result["tasks"][0]["skills"] == ["python-test"]
    assert result["tasks"][0]["filesToRead"] == drafts["tasks"][0]["filesToRead"]
    assert len(ranker.calls) == 1
    assert ranker.calls[0][1][0].description == "Description for python-test"


def test_ranker_failure_leaves_no_task_file(tmp_path: Path) -> None:
    class Broken:
        def rank(self, *_args):
            raise RuntimeError("model unavailable")

    with pytest.raises(RuntimeError, match="model unavailable"):
        core.generate_task_json(
            _drafts(),
            "ranked",
            project_root=tmp_path,
            skills_index=_ranked_index(tmp_path),
            ranker=Broken(),
            assignment_mode="qwen",
        )
    assert not (tmp_path / ".tasks").exists()


def test_pair_preflight_runs_before_ranker_factory(tmp_path: Path) -> None:
    calls: list[str] = []

    def reject_pairs(_tasks, _candidates) -> None:
        calls.append("preflight")
        raise ValueError("pair too large")

    def factory(_candidates):
        calls.append("factory")
        return FakeRanker(("python-test",))

    with pytest.raises(ValueError, match="pair too large"):
        core.generate_task_json(
            _drafts(),
            "ranked",
            project_root=tmp_path,
            skills_index=_ranked_index(tmp_path),
            ranker_factory=factory,
            assignment_mode="qwen",
            pair_preflight=reject_pairs,
        )
    assert calls == ["preflight"]
    assert not (tmp_path / ".tasks").exists()


def test_shadow_requires_diagnostics_sink(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="diagnostics sink"):
        core.generate_task_json(
            _drafts(),
            "shadow",
            project_root=tmp_path,
            skills_index=_ranked_index(tmp_path),
            ranker=FakeRanker(("python-test",)),
            assignment_mode="shadow",
        )


def test_packet_diagnostics_are_atomic_and_complete(tmp_path: Path) -> None:
    drafts = _drafts()
    drafts["tasks"].append(
        {
            **drafts["tasks"][0],
            "purpose": "Write more Python tests.",
        }
    )
    ranker = FakeRanker(("python-test",))
    diagnostics = tmp_path / "diagnostics.json"
    output = core.generate_task_json(
        drafts,
        "ranked",
        project_root=tmp_path,
        skills_index=_ranked_index(tmp_path),
        ranker=ranker,
        assignment_mode="qwen",
        diagnostic_sink=AtomicDiagnosticSink(diagnostics),
    )
    payload = json.loads(diagnostics.read_text(encoding="utf-8"))
    assert output.exists()
    assert len(payload["records"]) == 2
    assert payload["records"][0]["model_hash"] != payload["records"][0]["runtime_hash"]


def test_existing_diagnostic_is_preserved_and_blocks_task(tmp_path: Path) -> None:
    diagnostics = tmp_path / "diagnostics.json"
    diagnostics.write_text("preserve", encoding="utf-8")
    with pytest.raises(RuntimeError, match="already exists"):
        core.generate_task_json(
            _drafts(),
            "ranked",
            project_root=tmp_path,
            skills_index=_ranked_index(tmp_path),
            ranker=FakeRanker(("python-test",)),
            assignment_mode="qwen",
            diagnostic_sink=AtomicDiagnosticSink(diagnostics),
        )
    assert diagnostics.read_text(encoding="utf-8") == "preserve"
    assert not (tmp_path / ".tasks").exists()


def test_generate_task_json_writes_to_explicit_output_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(core.time, "time_ns", lambda: 1_700_000_000_123_000_000)
    output_dir = tmp_path / "state"
    output = core.generate_task_json(
        _drafts(),
        "generate-tests",
        output_dir=output_dir,
        skills_index=[
            {"name": "python-test", "class": "operation", **STRUCTURED_INDEX}
        ],
    )
    assert output == output_dir / "1700000000123-generate-tests.json"


def test_generate_task_json_writes_to_explicit_output_file(tmp_path: Path) -> None:
    output = core.generate_task_json(
        _drafts(),
        output_file=tmp_path / "plan" / "tasks.json",
        skills_index=[
            {"name": "python-test", "class": "operation", **STRUCTURED_INDEX}
        ],
    )
    assert output == tmp_path / "plan" / "tasks.json"


def test_generate_task_json_rejects_mixed_destination_modes(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="mutually exclusive"):
        core.generate_task_json(
            _drafts(),
            "generate-tests",
            output_file=tmp_path / "tasks.json",
            skills_index=[
                {"name": "python-test", "class": "operation", **STRUCTURED_INDEX}
            ],
        )


def test_generate_task_json_rejects_non_json_explicit_output(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match=".json suffix"):
        core.generate_task_json(
            _drafts(),
            output_file=tmp_path / "tasks.txt",
            skills_index=[
                {"name": "python-test", "class": "operation", **STRUCTURED_INDEX}
            ],
        )


def test_generate_task_json_rejects_invalid_input_without_replacing_output(
    tmp_path: Path,
) -> None:
    output = tmp_path / ".tasks" / "generate-tests.json"
    output.parent.mkdir()
    output.write_text('{"preserve": true}\n')
    with pytest.raises(core.GenerationValidationError, match="input failed"):
        core.generate_task_json(
            {"summary": "missing tasks"},
            "generate-tests",
            project_root=tmp_path,
        )
    assert output.read_text() == '{"preserve": true}\n'


def test_generate_task_json_rejects_context_below_minimum(tmp_path: Path) -> None:
    drafts = _drafts()
    drafts["tasks"][0]["context"] = "x" * 199
    with pytest.raises(core.GenerationValidationError, match="input failed"):
        core.generate_task_json(
            drafts,
            "generate-tests",
            project_root=tmp_path,
            skills_index=[
                {"name": "python-test", "class": "operation", **STRUCTURED_INDEX}
            ],
        )
    assert not (tmp_path / ".tasks").exists()


def test_generate_task_json_rejects_draft_skills_before_creating_tasks_directory(
    tmp_path: Path,
) -> None:
    drafts = _drafts()
    drafts["tasks"][0]["skills"] = ["manual-skill"]
    with pytest.raises(core.GenerationValidationError, match="input failed"):
        core.generate_task_json(drafts, "generate-tests", project_root=tmp_path)
    assert not (tmp_path / ".tasks").exists()


def test_generate_task_json_allows_missing_candidates(tmp_path: Path) -> None:
    output = core.generate_task_json(
        _drafts(), "generate-tests", project_root=tmp_path, skills_index=[]
    )
    result = json.loads(output.read_text())
    assert result["tasks"][0]["skills"] == []


def test_generate_task_json_rejects_invalid_final_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    validations = iter([[], ["final output is invalid"]])
    monkeypatch.setattr(core, "validate_json_schema", lambda *_: next(validations))
    with pytest.raises(core.GenerationValidationError, match="output failed"):
        core.generate_task_json(
            _drafts(),
            "generate-tests",
            project_root=tmp_path,
            skills_index=[{"name": "test", "class": "operation", **STRUCTURED_INDEX}],
        )


def test_candidate_skills_discovers_and_filters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        core,
        "_discover_skills",
        lambda: [_skill(), _skill("planner", "planning")],
    )
    assert [skill.name for skill in core._candidate_skills(None)] == ["python-test"]


def test_parse_skills_preserves_structured_signature() -> None:
    parsed = core._parse_skills(
        [
            {
                "name": "minimal",
                "description": "Use when routing minimal tasks",
                "class": "operation",
                "schema_version": "1.0",
                "cues": [{"facet": "subject", "value": "minimal routing"}],
                "relationships": [{"role": "support"}],
            }
        ]
    )
    assert parsed[0].name == "minimal"
    assert parsed[0].cues[0].value == "minimal routing"


@pytest.mark.parametrize(
    ("updates", "message"),
    [
        ({"name": "not canonical"}, "canonical kebab-case"),
        ({"description": "unsafe\ntext"}, "safe single-line"),
        ({"class": "unknown"}, "class is invalid"),
    ],
)
def test_parse_skills_rejects_malformed_inventory_fields(updates, message) -> None:
    entry = {
        "name": "valid",
        "description": "Use when validating inventory",
        "class": "operation",
        **STRUCTURED_INDEX,
        **updates,
    }

    with pytest.raises(ValueError, match=message):
        core._parse_skills([entry])


def test_parse_skills_rejects_duplicate_inventory_names() -> None:
    entry = {
        "name": "duplicate",
        "description": "Use when validating inventory",
        "class": "operation",
        **STRUCTURED_INDEX,
    }

    with pytest.raises(ValueError, match="duplicate skill inventory name"):
        core._parse_skills([entry, entry.copy()])


def test_parse_skills_rejects_oversized_inventory() -> None:
    with pytest.raises(ValueError, match="128 entries"):
        core._parse_skills([{} for _ in range(129)])


def test_discover_skills_resolves_index() -> None:
    with patch("lib.generate_task_json.core.discover_all_skills") as discover:
        assert core._discover_skills() == []
    discover.assert_called_once()


def test_select_skills_uses_threshold_without_fallback() -> None:
    matching = _skill()
    weak = Skill(name="docs", description="", class_="documentation")
    task = _drafts()["tasks"][0]
    assert core._select_skills(task, [weak, matching]) == ["python-test"]
    assert core._select_skills(task, [weak]) == []
    assert core._select_skills(task, []) == []


def test_select_skills_does_not_select_a_class_only_match() -> None:
    """Do not assign unrelated skills solely because their class matches."""
    task = {
        "purpose": "Update the planning architecture reference.",
        "context": (
            "Revise the planning lifecycle reference skill frontmatter and required "
            "sections. Preserve passive reference content and validate the updated "
            "skill against authoring requirements without generating scripts or tests."
        ),
        "filesToRead": ["skills/planning-pipeline-architecture/SKILL.md"],
        "filesToWrite": ["skills/planning-pipeline-architecture/SKILL.md"],
        "executionInstructions": [{"step": 1, "action": "Update the reference."}],
        "expectedOutput": "A validated planning reference skill.",
    }
    factory = Skill(
        name="skill-factory",
        description="Create and update OpenCode skill files",
        cues=(
            RoutingCue("operation", "create-skill", primary=True),
            RoutingCue("subject", "frontmatter"),
        ),
        relationships=(RoutingRelationship("owner"),),
        class_="operation",
    )
    bash_tests = Skill(
        name="skill-script-bash-test-writer",
        description="Operate unrelated shell deployments",
        cues=(
            RoutingCue("operation", "write-tests", primary=True),
            RoutingCue("subject", "bash"),
        ),
        relationships=(RoutingRelationship("owner"),),
        class_="operation",
    )

    assert core._select_skills(task, [factory, bash_tests]) == ["skill-factory"]


def test_select_skills_caps_matches_at_three() -> None:
    task = _drafts()["tasks"][0]
    candidates = [_skill(f"python-test-{index}") for index in range(4)]
    assert core._select_skills(task, candidates) == [
        "python-test-0",
        "python-test-1",
        "python-test-2",
    ]


def test_task_text_and_scoring_helpers() -> None:
    task = _drafts()["tasks"][0]
    text = core._task_text(task)
    assert "Write Python tests." in text
    assert "Python tests." in text
    assert "scripts/python/src/cli/example.py" not in text
    assert "scripts/python/tests/test_example.py" not in text
    assert core._score_skill(_skill(), text) > core._score_skill(
        Skill(name="docs", description="docs", class_="documentation"), text
    )
    assert core._tokenize("Write WRITE tests!") == {"write", "tests"}
    assert core._infer_task_class({"document", "guide"}) == "documentation"
    assert core._infer_task_class({"write", "test"}) == "operation"


def test_task_text_excludes_file_paths() -> None:
    """File paths in filesToRead and filesToWrite are absent from scoring text."""
    task = _drafts()["tasks"][0]
    text = core._task_text(task)
    assert "scripts/python/src/cli/example.py" not in text
    assert "scripts/python/tests/test_example.py" not in text


def test_task_text_includes_expected_output() -> None:
    """expectedOutput content is present in the task scoring text."""
    task = _drafts()["tasks"][0]
    text = core._task_text(task)
    assert "Python tests." in text


def test_skill_assignment_ignores_misleading_file_paths() -> None:
    """A task touching skill-factory's SKILL.md must not assign skill-factory
    based on file-path tokens alone when purpose/context are unrelated."""
    task = {
        "purpose": "Fix a typo in the README",
        "context": (
            "Correct a typographical error in the project's main README file. "
            "This documentation guide contains a misspelled word that could "
            "confuse new users. The fix involves locating the exact line with "
            "the error, replacing the incorrect spelling, and verifying the "
            "change renders properly in the rendered output. No functional "
            "code changes are required. This is a straightforward documentation "
            "correction that improves the quality of the project's primary "
            "entry point for new contributors and serves as a reference for "
            "the entire project."
        ),
        "filesToRead": ["README.md"],
        "filesToWrite": ["skills/skill-factory/SKILL.md"],
        "executionInstructions": [{"step": 1, "action": "Fix the typo."}],
        "expectedOutput": "The README with the typo corrected.",
    }
    skill_factory = Skill(
        name="skill-factory",
        description="Create and manage OpenCode skills",
        cues=(
            RoutingCue("operation", "create-skill", primary=True),
            RoutingCue("subject", "opencode-skill"),
        ),
        relationships=(RoutingRelationship("owner"),),
        class_="operation",
    )
    readme_editor = Skill(
        name="readme-editor",
        description="Fix typo and formatting error in documentation and README file",
        cues=(
            RoutingCue("operation", "fix-typo", primary=True),
            RoutingCue("subject", "readme"),
        ),
        relationships=(RoutingRelationship("owner"),),
        class_="documentation",
    )
    selected = core._select_skills(task, [skill_factory, readme_editor])
    assert "skill-factory" not in selected
    assert "readme-editor" in selected


def test_score_skill_tokenizes_compound_tags() -> None:
    """Hyphenated tags contribute their individual terms to tag similarity."""
    matching = Skill(
        name="workspace",
        description="",
        cues=(
            RoutingCue("operation", "create-workspace", primary=True),
            RoutingCue("subject", "plan-workspace", ("workspace",)),
            RoutingCue("outcome", "task-json"),
        ),
        relationships=(RoutingRelationship("owner"),),
        class_="operation",
    )
    unrelated = Skill(
        name="proposal",
        description="",
        cues=(
            RoutingCue("operation", "write-proposal", primary=True),
            RoutingCue("subject", "decision-record"),
        ),
        relationships=(RoutingRelationship("owner"),),
        class_="operation",
    )

    assert core._score_skill(matching, "create a plan workspace") > core._score_skill(
        unrelated,
        "create a plan workspace",
    )


def test_output_path_prefixes_slug_with_epoch_milliseconds(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(core.time, "time_ns", lambda: 1_700_000_000_123_000_000)
    assert core._output_path("generate-tests", tmp_path / ".tasks") == (
        tmp_path / ".tasks" / "1700000000123-generate-tests.json"
    )


def test_output_path_rejects_invalid_slug(tmp_path: Path) -> None:
    with pytest.raises(core.SummarySlugError, match="kebab-case"):
        core._output_path("not/a-slug", tmp_path / ".tasks")


def test_derive_slug_from_summary() -> None:
    """Verbs and nouns in the summary become a valid kebab-case slug."""
    assert (
        core._derive_slug("Generate test task packets.") == "generate-test-task-packets"
    )
    assert core._derive_slug("  Hello   World  ") == "hello-world"
    assert core._derive_slug("Special!@#Chars___Here") == "specialcharshere"
    assert core._derive_slug("---leading and trailing---") == "leading-and-trailing"


def test_derive_slug_returns_none_for_invalid_summary() -> None:
    """A summary that produces no valid slug characters returns None."""
    assert core._derive_slug("!!!") is None
    assert core._derive_slug("") is None


def test_generate_task_json_derives_slug_from_summary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(core.time, "time_ns", lambda: 1_700_000_000_123_000_000)
    drafts = _drafts()  # summary is "Generate test task packets."
    output = core.generate_task_json(
        drafts,
        summary_slug=None,
        project_root=tmp_path,
        skills_index=[
            {
                "name": "python-test",
                "description": "Write Python tests",
                "class": "operation",
                **STRUCTURED_INDEX,
            }
        ],
    )
    assert output.name == "1700000000123-generate-test-task-packets.json"


def test_write_json_new_cleans_up_after_link_failure(
    tmp_path: Path,
) -> None:
    output = tmp_path / "output.json"
    with (
        patch("lib.generate_task_json.core.os.link", side_effect=OSError("boom")),
        pytest.raises(OSError, match="boom"),
    ):
        core._write_json_new(output, {"key": "value"})
    assert list(tmp_path.glob(".output.json.tmp_*")) == []
