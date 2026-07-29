"""CLI integration tests for generate-task-json."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from cli import generate_task_json
from lib.generate_task_json.core import GenerationValidationError
from lib.generate_task_json.ranker import ScoreResult

VALID_CONTEXT = (
    "Exercise the CLI task generator with a complete draft that identifies the test "
    "scope, target behavior, expected output, and relevant constraints while avoiding "
    "unrelated code changes or unsupported execution paths."
)


def _drafts() -> str:
    return json.dumps(
        {
            "summary": "CLI test.",
            "tasks": [
                {
                    "purpose": "Write tests.",
                    "context": VALID_CONTEXT,
                    "filesToRead": [],
                    "filesToWrite": [],
                    "executionInstructions": [{"step": 1, "action": "Write tests."}],
                    "expectedOutput": "Tests.",
                }
            ],
        }
    )


def _skills_file(tmp_path: Path) -> Path:
    path = tmp_path / "skills.json"
    skill = tmp_path / "python-test" / "SKILL.md"
    skill.parent.mkdir(parents=True, exist_ok=True)
    skill.write_text("skill", encoding="utf-8")
    path.write_text(
        json.dumps(
            [
                {
                    "name": "python-test",
                    "description": "Write Python tests",
                    "tags": ["python", "tests"],
                    "class": "operation",
                    "source": "project",
                    "path": str(skill),
                }
            ]
        )
    )
    return path


def _with_skills(arguments: list[str], path: Path) -> list[str]:
    return ["--skills-file", str(path), *arguments]


def test_help() -> None:
    result = CliRunner().invoke(generate_task_json.main, ["--help"])
    assert result.exit_code == 0
    assert "Assign skills" in result.output


def test_skills_file_is_required() -> None:
    result = CliRunner().invoke(
        generate_task_json.main,
        ["--assignment-mode", "lexical", "--output-dir", ".tasks"],
        input=_drafts(),
    )
    assert result.exit_code == 2
    assert "Missing option '--skills-file'" in result.output


def test_skills_file_must_be_a_bare_array(tmp_path: Path) -> None:
    skills = tmp_path / "skills.json"
    skills.write_text(json.dumps({"skills": []}), encoding="utf-8")
    result = CliRunner().invoke(
        generate_task_json.main,
        _with_skills(
            ["--assignment-mode", "lexical", "--output-dir", ".tasks"], skills
        ),
        input=_drafts(),
    )
    assert result.exit_code == 2
    assert "bare JSON array" in result.output


def test_success_prints_relative_output_path(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        generate_task_json,
        "generate_task_json",
        lambda _data, slug, *, output_dir, output_file, **_kwargs: (
            output_file,
            output_dir / f"1700000000123-{slug}.json",
        )[1],
    )
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        skills = _skills_file(Path.cwd())
        result = runner.invoke(
            generate_task_json.main,
            _with_skills(
                [
                    "--summary-slug",
                    "cli-test",
                    "--output-dir",
                    str(Path.cwd() / ".tasks"),
                ],
                skills,
            ),
            input=_drafts(),
        )
    assert result.exit_code == 0
    assert result.output == ".tasks/1700000000123-cli-test.json\n"


def test_missing_summary_slug_is_derived_from_summary(tmp_path, monkeypatch) -> None:
    from lib.generate_task_json.core import _derive_slug

    monkeypatch.setattr(
        generate_task_json,
        "generate_task_json",
        lambda _data, _slug, *, output_dir, **_kwargs: (
            output_dir / f"1700000000123-{_derive_slug(_data['summary'])}.json"
        ),
    )
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        skills = _skills_file(Path.cwd())
        result = runner.invoke(
            generate_task_json.main,
            _with_skills(["--output-dir", str(Path.cwd() / ".tasks")], skills),
            input=_drafts(),
        )
    assert result.exit_code == 0
    assert result.output == ".tasks/1700000000123-cli-test.json\n"


def test_success_uses_preserved_pwd_after_uv_directory_change(
    tmp_path, monkeypatch
) -> None:
    workspace = tmp_path / "workspace"
    output_dir = workspace / ".tasks"
    workspace.mkdir()
    monkeypatch.setenv("PWD", str(workspace))
    monkeypatch.setattr(
        generate_task_json,
        "generate_task_json",
        lambda _data, _slug, *, output_dir, **_kwargs: (
            output_dir / "1700000000123-cli-test.json"
        ),
    )
    skills = _skills_file(workspace)

    result = CliRunner().invoke(
        generate_task_json.main,
        _with_skills(
            ["--summary-slug", "cli-test", "--output-dir", str(output_dir)], skills
        ),
        input=_drafts(),
    )

    assert result.exit_code == 0, result.output
    assert result.output == ".tasks/1700000000123-cli-test.json\n"


def test_missing_output_dir_fails() -> None:
    result = CliRunner().invoke(
        generate_task_json.main, ["--summary-slug", "cli-test"], input=_drafts()
    )
    assert result.exit_code == 2


def test_explicit_output_file_succeeds(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        generate_task_json,
        "generate_task_json",
        lambda _data, _slug, *, output_dir, output_file, **_kwargs: (
            output_dir,
            output_file,
        )[1],
    )
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        output_file = Path.cwd() / "tasks.json"
        skills = _skills_file(Path.cwd())
        result = runner.invoke(
            generate_task_json.main,
            _with_skills(["--output-file", str(output_file)], skills),
            input=_drafts(),
        )
    assert result.exit_code == 0
    assert result.output == "tasks.json\n"


def test_explicit_output_file_outside_cwd_fails(tmp_path: Path) -> None:
    skills = _skills_file(tmp_path)
    result = CliRunner().invoke(
        generate_task_json.main,
        _with_skills(["--output-file", str(tmp_path / "tasks.json")], skills),
        input=_drafts(),
    )
    assert result.exit_code == 2
    assert "within the current working directory" in result.output


def test_partial_or_mixed_destination_options_fail() -> None:
    runner = CliRunner()
    for arguments in (
        [],
        ["--summary-slug", "cli-test"],
        [
            "--summary-slug",
            "cli-test",
            "--output-dir",
            ".tasks",
            "--output-file",
            "tasks.json",
        ],
    ):
        result = runner.invoke(generate_task_json.main, arguments, input=_drafts())
        assert result.exit_code == 2


def test_invalid_summary_slug_fails() -> None:
    # Click's required inventory check is covered separately.
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as directory:
        skills = _skills_file(Path(directory))
        result = CliRunner().invoke(
            generate_task_json.main,
            _with_skills(
                [
                    "--assignment-mode",
                    "lexical",
                    "--summary-slug",
                    "Not a slug",
                    "--output-dir",
                    ".tasks",
                ],
                skills,
            ),
            input=_drafts(),
        )
    assert result.exit_code == 2
    assert "kebab-case" in result.output


def test_malformed_json_fails() -> None:
    result = CliRunner().invoke(
        generate_task_json.main,
        ["--summary-slug", "cli-test", "--output-dir", ".tasks"],
        input="not json",
    )
    assert result.exit_code == 2
    assert "Error:" in result.output


def test_array_json_fails() -> None:
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as directory:
        skills = _skills_file(Path(directory))
        result = CliRunner().invoke(
            generate_task_json.main,
            _with_skills(
                ["--summary-slug", "cli-test", "--output-dir", ".tasks"], skills
            ),
            input="[]",
        )
    assert result.exit_code == 2
    assert "object" in result.output


def test_validation_failure_has_no_stdout(monkeypatch) -> None:
    monkeypatch.setattr(
        generate_task_json,
        "generate_task_json",
        lambda *_, **__: (_ for _ in ()).throw(
            GenerationValidationError("invalid draft")
        ),
    )
    with __import__("tempfile").TemporaryDirectory() as directory:
        skills = _skills_file(Path(directory))
        result = CliRunner().invoke(
            generate_task_json.main,
            _with_skills(
                ["--summary-slug", "cli-test", "--output-dir", ".tasks"], skills
            ),
            input=_drafts(),
        )
    assert result.exit_code == 2
    assert result.output == "Error: invalid draft\n"


def test_runtime_failure_fails(monkeypatch) -> None:
    monkeypatch.setattr(
        generate_task_json,
        "generate_task_json",
        lambda *_, **__: (_ for _ in ()).throw(RuntimeError("no skills")),
    )
    with __import__("tempfile").TemporaryDirectory() as directory:
        skills = _skills_file(Path(directory))
        result = CliRunner().invoke(
            generate_task_json.main,
            _with_skills(
                ["--summary-slug", "cli-test", "--output-dir", ".tasks"], skills
            ),
            input=_drafts(),
        )
    assert result.exit_code == 1


def test_output_error_fails(monkeypatch) -> None:
    monkeypatch.setattr(
        generate_task_json,
        "generate_task_json",
        lambda *_, **__: (_ for _ in ()).throw(OSError("bad path")),
    )
    with __import__("tempfile").TemporaryDirectory() as directory:
        skills = _skills_file(Path(directory))
        result = CliRunner().invoke(
            generate_task_json.main,
            _with_skills(
                ["--assignment-mode", "lexical", "--output-dir", ".tasks"],
                skills,
            ),
            input=_drafts(),
        )
    assert result.exit_code == 1


def test_lexical_mode_does_not_load_ranker_manifest(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        generate_task_json,
        "load_manifest",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("loaded")),
    )
    result = CliRunner().invoke(
        generate_task_json.main,
        _with_skills(
            [
                "--assignment-mode",
                "lexical",
                "--project-root",
                str(tmp_path),
                "--output-file",
                str(Path.cwd() / "lexical-test.json"),
            ],
            _skills_file(tmp_path),
        ),
        input=_drafts(),
    )
    assert result.exit_code == 0, result.output
    Path("lexical-test.json").unlink()


def test_shadow_requires_diagnostics_file(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        generate_task_json.main,
        _with_skills(
            [
                "--assignment-mode",
                "shadow",
                "--project-root",
                str(tmp_path),
                "--output-dir",
                str(tmp_path / ".tasks"),
            ],
            _skills_file(tmp_path),
        ),
        input=_drafts(),
    )
    assert result.exit_code == 2
    assert "requires --diagnostics-file" in result.output


def test_qwen_mode_accepts_external_project_inventory(
    tmp_path: Path,
    monkeypatch,
) -> None:
    class FakeScorer:
        last_token_counts = (100,)
        last_request_seconds = (0.01,)
        last_prompt_hashes = ("a" * 64,)

        def __init__(self, *_args, **_kwargs) -> None:
            pass

        def score(self, _query, documents):
            return [ScoreResult(0.9) for _ in documents]

        def diagnostic_identity(self):
            return {
                "model": "model",
                "runtime": "runtime",
                "tokenizer": "tokenizer",
                "prompt": "prompt",
                "render": "render",
            }

    monkeypatch.setattr(generate_task_json, "OllamaQwenScorer", FakeScorer)
    output_dir = tmp_path / ".tasks"
    diagnostics = tmp_path / "diagnostics.json"
    result = CliRunner().invoke(
        generate_task_json.main,
        _with_skills(
            [
                "--assignment-mode",
                "qwen",
                "--project-root",
                str(tmp_path),
                "--diagnostics-file",
                str(diagnostics),
                "--output-dir",
                str(output_dir),
            ],
            _skills_file(tmp_path),
        ),
        input=_drafts(),
    )
    assert result.exit_code == 0, result.output
    output = next(output_dir.glob("*.json"))
    assert json.loads(output.read_text())["tasks"][0]["skills"] == ["python-test"]
    assert len(json.loads(diagnostics.read_text())["records"]) == 1
