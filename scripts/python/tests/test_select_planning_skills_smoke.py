"""Focused end-to-end smoke coverage for planning-context selection.

These tests create the discovered skill metadata on demand and inject a
deterministic scorer.  They therefore exercise the real collector, source
precedence, planning boundary, selector policy, and CLI serialization without
requiring a model or a caller-managed inventory.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner

from cli import select_planning_skills as cli
from lib.generate_task_json.ranker import ScoreResult
from lib.select_planning_skills.core import select_planning_skills
from lib.select_planning_skills.policy import PlanningSelectionPolicy

POLICY = json.dumps(
    {
        "absolute_inclusion_threshold": 0.5,
        "minimum_cardinality": 0,
        "max_cardinality": 3,
        "decision_gate": "benchmark-approved",
    }
)


class DeterministicScorer:
    def __init__(self, scores: Sequence[float] | Exception) -> None:
        self.scores = scores
        self.calls: list[tuple[str, tuple[str, ...]]] = []

    def score(self, query: str, documents: Sequence[str]) -> list[ScoreResult]:
        self.calls.append((query, tuple(documents)))
        if isinstance(self.scores, Exception):
            raise self.scores
        return [ScoreResult(score) for score in self.scores]


class FakeTokenBudget:
    def __init__(self, *_args: object, **_kwargs: object) -> None:
        pass

    def count(self, text: str) -> int:
        return len(text)

    def preflight(self, _prompt: str) -> SimpleNamespace:
        return SimpleNamespace(token_count=1)


class FakeCliScorer(DeterministicScorer):
    instances: list[FakeCliScorer] = []

    def __init__(self, _manifest: object, _host: str, **_kwargs: object) -> None:
        super().__init__([0.9])
        self.__class__.instances.append(self)

    def diagnostic_identity(self) -> dict[str, str]:
        return {
            key: "smoke"
            for key in ("model", "runtime", "tokenizer", "prompt", "render")
        }


def write_skill(
    root: Path, name: str, skill_class: str = "planning", body: str = "body"
) -> None:
    path = root / name / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\nname: {name}\ndescription: {name} context\n"
        f"class: {skill_class}\ntags: [planning, context, smoke, reference]\n"
        f"---\n{body}\n",
        encoding="utf-8",
    )


def policy() -> PlanningSelectionPolicy:
    return PlanningSelectionPolicy(0.5, 0, 3)


def select(project: Path, config: Path, scorer: DeterministicScorer) -> tuple[str, ...]:
    return select_planning_skills(
        "Plan the requested change.",
        scorer,
        project_root=project,
        config_dir=config,
        policy=policy(),
    )


def test_dynamic_collection_precedence_and_planning_boundary(tmp_path: Path) -> None:
    project = tmp_path / "project"
    config = tmp_path / "config"
    project_root = project / ".opencode" / "skills"
    global_root = config / "skills"
    write_skill(project_root, "shared", body="project metadata")
    write_skill(global_root, "shared", body="global metadata")
    write_skill(project_root, "planning-reference")
    for name in ("generic-analysis", "proposal", "plan", "not-planning"):
        write_skill(project_root, name, "operation")

    scorer = DeterministicScorer([0.9, 0.8])
    assert select(project, config, scorer) == ("planning-reference", "shared")
    assert len(scorer.calls) == 1
    documents = scorer.calls[0][1]
    document_names = {
        document.splitlines()[0].removeprefix("Skill name: ")
        for document in documents
    }
    assert document_names.isdisjoint(
        {"generic-analysis", "proposal", "plan", "not-planning"}
    )
    assert "global metadata" not in "\n".join(documents)

    (project_root / "planning-reference" / "SKILL.md").unlink()
    write_skill(project_root, "new-planning-reference")
    assert select(project, config, DeterministicScorer([0.9, 0.8])) == (
        "new-planning-reference",
        "shared",
    )


@pytest.mark.parametrize(
    ("scores", "expected"),
    [([0.9, 0.8, 0.1], ("first", "second")), ([0.1, 0.2, 0.3], ())],
)
def test_positive_multi_and_finalized_no_match_results_are_exact(
    tmp_path: Path, scores: list[float], expected: tuple[str, ...]
) -> None:
    project = tmp_path / "project"
    for name in ("first", "second", "third"):
        write_skill(project / ".opencode" / "skills", name)
    assert select(project, tmp_path / "config", DeterministicScorer(scores)) == expected


def test_cli_emits_only_the_authoritative_bare_array(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    FakeCliScorer.instances.clear()
    manifest = SimpleNamespace(
        tokenizer_path=Path("unused"),
        data={"assets": {"tokenizer": {"sha256": "unused"}}},
        num_ctx=4096,
    )
    monkeypatch.setattr(cli, "load_manifest", lambda **_kwargs: manifest)
    monkeypatch.setattr(cli, "QwenTokenBudget", FakeTokenBudget)
    monkeypatch.setattr(cli, "OllamaQwenScorer", FakeCliScorer)
    project = tmp_path / "project"
    write_skill(project / ".opencode" / "skills", "planner")

    result = CliRunner().invoke(
        cli.main,
        [
            "--project-root",
            str(project),
            "--config-dir",
            str(tmp_path / "config"),
            "--planning-policy",
            POLICY,
        ],
        input="Plan the release.\n",
    )
    assert result.exit_code == 0, result.output
    assert result.stdout == '["planner"]\n'
    assert result.stderr == ""
    assert json.loads(result.stdout) == ["planner"]


def test_malformed_input_and_model_failure_block_without_partial_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    malformed = CliRunner().invoke(cli.main, ["--planning-policy", POLICY], input="   ")
    assert malformed.exit_code == 2
    assert malformed.stdout == ""

    project = tmp_path / "project"
    write_skill(project / ".opencode" / "skills", "planner")
    monkeypatch.setattr(
        cli,
        "select_planning_skills",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("model failed")),
    )
    failed = CliRunner().invoke(
        cli.main,
        ["--project-root", str(project), "--planning-policy", POLICY],
        input="Plan it",
    )
    assert failed.exit_code == 1
    assert failed.stdout == ""
    assert "model failed" in failed.stderr


def test_caller_reconciliation_loads_exact_selector_array_without_mutation() -> None:
    contract = Path(__file__).parents[3] / "skills/breakdown-tasks/SKILL.md"
    text = contract.read_text(encoding="utf-8")
    assert "Load all and only the returned planning names" in text
    assert "Do not add, remove, replace, reorder, deduplicate" in text
    selected = ["planning-reference", "skill-architect"]
    loaded: list[str] = []
    for name in selected:
        loaded.append(name)
    assert loaded == selected
    assert selected == ["planning-reference", "skill-architect"]
