"""CLI integration tests for select-planning-skills.

The model and tokenizer are replaced at the CLI boundary so these tests never
contact Ollama or depend on the installed manifest assets.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from click.testing import CliRunner

from cli import select_planning_skills
from lib.generate_task_json.ranker import ScoreResult

POLICY = json.dumps(
    {
        "absolute_inclusion_threshold": 0.5,
        "minimum_cardinality": 0,
        "max_cardinality": 3,
        "decision_gate": "benchmark-approved",
    }
)


class FakeTokenBudget:
    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        self.preflight_calls: list[str] = []

    def count(self, text: str) -> int:
        return len(text)

    def preflight(self, prompt: str) -> SimpleNamespace:
        self.preflight_calls.append(prompt)
        return SimpleNamespace(token_count=len(prompt))


class FakeScorer:
    instances: list[FakeScorer] = []

    def __init__(self, _manifest: Any, host: str, **kwargs: Any) -> None:
        self.host = host
        self.kwargs = kwargs
        self.calls: list[tuple[str, tuple[str, ...]]] = []
        self.__class__.instances.append(self)

    def score(self, query: str, documents: tuple[str, ...]) -> list[ScoreResult]:
        self.calls.append((query, documents))
        return [ScoreResult(0.9) for _ in documents]

    def diagnostic_identity(self) -> dict[str, str]:
        return {
            "model": "model-hash",
            "runtime": "runtime-hash",
            "tokenizer": "tokenizer-hash",
            "prompt": "prompt-hash",
            "render": "render-hash",
        }


@pytest.fixture(autouse=True)
def deterministic_model(monkeypatch: pytest.MonkeyPatch) -> None:
    FakeScorer.instances.clear()
    manifest = SimpleNamespace(
        tokenizer_path=Path("unused-tokenizer"),
        data={"assets": {"tokenizer": {"sha256": "unused"}}},
        num_ctx=4096,
    )
    monkeypatch.setattr(select_planning_skills, "load_manifest", lambda **_: manifest)
    monkeypatch.setattr(select_planning_skills, "QwenTokenBudget", FakeTokenBudget)
    monkeypatch.setattr(select_planning_skills, "OllamaQwenScorer", FakeScorer)


def _skill(root: Path, name: str, description: str = "Plan work") -> Path:
    path = root / name / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        f"---\nname: {name}\n"
        f"description: {description}\nclass: planning\n"
        "tags: [plan, planning, selection, context]\n---\n",
        encoding="utf-8",
    )
    return path


def _args(*extra: str) -> list[str]:
    return ["--planning-policy", POLICY, *extra]


def test_complete_stdin_emits_exact_bare_array(tmp_path: Path) -> None:
    project = tmp_path / "project"
    _skill(project / ".opencode" / "skills", "planner")
    result = CliRunner().invoke(
        select_planning_skills.main,
        _args("--project-root", str(project), "--config-dir", str(tmp_path / "config")),
        input="Write a plan for the release.\n",
    )
    assert result.exit_code == 0, result.output
    assert result.stdout == '["planner"]\n'
    assert json.loads(result.stdout) == ["planner"]
    assert result.stderr == ""


@pytest.mark.parametrize("input_text", ["", "   ", b"\xff"])
def test_empty_or_malformed_stdin_fails_without_stdout(
    input_text: str | bytes,
) -> None:
    result = CliRunner().invoke(
        select_planning_skills.main, _args(), input=input_text
    )
    assert result.exit_code == 2
    assert result.stdout == ""
    assert result.stderr.startswith("Error:")


def test_project_and_config_roots_and_profile_reach_scorer(tmp_path: Path) -> None:
    project = tmp_path / "project"
    config = tmp_path / "config"
    _skill(project / ".claude" / "skills", "project-planner")
    _skill(config / "skills", "global-planner")
    result = CliRunner().invoke(
        select_planning_skills.main,
        _args(
            "--project-root",
            str(project),
            "--config-dir",
            str(config),
            "--model-profile",
            "q4",
        ),
        input="Plan it",
    )
    assert result.exit_code == 0, result.output
    assert set(json.loads(result.stdout)) == {"project-planner", "global-planner"}
    scorer = FakeScorer.instances[-1]
    assert scorer.kwargs["policy_identity"]


@pytest.mark.parametrize(
    "host", ["http://example.test:11434", "http://127.0.0.1:11434/path"]
)
def test_non_loopback_or_path_host_is_rejected(
    host: str,
) -> None:
    # Use the production scorer's constructor validation while keeping all
    # successful scoring deterministic and offline.
    from lib.generate_task_json.ollama_ranker import OllamaQwenScorer

    select_planning_skills.OllamaQwenScorer = OllamaQwenScorer
    result = CliRunner().invoke(
        select_planning_skills.main,
        _args("--ollama-host", host),
        input="Plan it",
    )
    assert result.exit_code == 2
    assert result.stdout == ""
    assert "loopback" in result.stderr or "path" in result.stderr


def test_policy_must_be_an_approved_exact_object() -> None:
    for policy in ["[]", json.dumps({**json.loads(POLICY), "extra": True})]:
        result = CliRunner().invoke(
            select_planning_skills.main,
            ["--planning-policy", policy],
            input="Plan it",
        )
        assert result.exit_code == 2
        assert result.stdout == ""
        assert "Error:" in result.stderr


def test_configured_zero_minimum_returns_empty_success_array(tmp_path: Path) -> None:
    empty_policy = json.dumps({**json.loads(POLICY), "minimum_cardinality": 0})
    result = CliRunner().invoke(
        select_planning_skills.main,
        [
            "--planning-policy",
            empty_policy,
            "--project-root",
            str(tmp_path),
            "--config-dir",
            str(tmp_path / "config"),
        ],
        input="Plan it",
    )
    assert result.exit_code == 0
    assert result.stdout == "[]\n"


def test_diagnostics_are_published_without_leaking_input(tmp_path: Path) -> None:
    diagnostic = tmp_path / "diagnostics.json"
    secret = "do not publish this task body"
    result = CliRunner().invoke(
        select_planning_skills.main,
        _args(
            "--diagnostics-file",
            str(diagnostic),
            "--config-dir",
            str(tmp_path / "config"),
        ),
        input=secret,
    )
    assert result.exit_code == 0
    payload = json.loads(diagnostic.read_text(encoding="utf-8"))
    assert payload["selected_names"] == []
    assert secret not in diagnostic.read_text(encoding="utf-8")


def test_failure_leaves_no_success_artifact_and_stderr_is_separate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        select_planning_skills,
        "select_planning_skills",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("scorer failed")),
    )
    diagnostic = tmp_path / "diagnostics.json"
    result = CliRunner().invoke(
        select_planning_skills.main,
        _args("--diagnostics-file", str(diagnostic)),
        input="Plan it",
    )
    assert result.exit_code == 1
    assert result.stdout == ""
    assert "scorer failed" in result.stderr
    assert not diagnostic.exists()


def test_no_caller_managed_skills_file_option() -> None:
    result = CliRunner().invoke(
        select_planning_skills.main,
        ["--help"],
    )
    assert result.exit_code == 0
    assert "--skills-file" not in result.stdout
    rejected = CliRunner().invoke(
        select_planning_skills.main,
        ["--skills-file", "skills.json", "--planning-policy", POLICY],
        input="Plan it",
    )
    assert rejected.exit_code == 2
    assert rejected.stdout == ""
