"""Direct-call coverage for command callbacks and their adapter contracts."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
import yaml

from cli import (
    agent_eval_suite,
    collect_skills,
    evaluate_semantic_selection,
    get_task,
    resolve_script_root,
    skill_validator,
    validate_skill_md,
    validate_skill_meta,
)
from lib.collect_skills.models import Skill, SkillIndex
from lib.semantic_selection_evaluation.core import EvaluationError

pytestmark = pytest.mark.unit


def _agent_options(task_path: Path) -> dict[str, Any]:
    return {
        "list_cases": False,
        "write_inspect_task": task_path,
        "run_inspect": False,
        "inspect_model": None,
        "inspect_log_dir": None,
        "inspect_limit": None,
        "run_terminal_bench": False,
        "tb_agent": "opencode",
        "tb_agent_import_path": None,
        "tb_agent_kwarg": (),
        "tb_model": None,
        "tb_dataset": "terminal-bench-core==0.1.1",
        "tb_output_path": Path("/tmp/opencode/terminal-bench-runs"),
        "tb_task_id": (),
        "tb_n_tasks": None,
        "tb_n_concurrent": 1,
        "tb_no_rebuild": False,
        "tb_no_cleanup": False,
    }


def test_agent_eval_callback_lists_cases_and_serializes_process_results(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Keep framework checks, task creation, and process results observable."""
    task_path = tmp_path / "task.py"
    monkeypatch.setattr(
        agent_eval_suite,
        "preflight_frameworks",
        lambda: SimpleNamespace(
            inspect_ai="1.0",
            terminal_bench="2.0",
            tb_executable="/bin/tb",
        ),
    )
    monkeypatch.setattr(
        agent_eval_suite, "list_eval_cases", lambda: [{"case_id": "a"}]
    )
    monkeypatch.setattr(
        agent_eval_suite, "write_inspect_task_file", lambda _: task_path
    )
    monkeypatch.setattr(
        agent_eval_suite,
        "run_inspect_eval",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0, stdout="inspect ok", stderr=""
        ),
    )
    monkeypatch.setattr(
        agent_eval_suite,
        "run_terminal_bench_eval",
        lambda **_kwargs: SimpleNamespace(
            returncode=0, stdout="bench ok", stderr="warning"
        ),
    )
    options = _agent_options(task_path)
    options.update(
        list_cases=True,
        run_inspect=True,
        inspect_model="provider/model",
        inspect_log_dir=tmp_path / "logs",
        inspect_limit=4,
        run_terminal_bench=True,
        tb_model="ollama/model",
        tb_agent_kwarg=("temperature=0",),
        tb_task_id=("one",),
        tb_n_tasks=1,
        tb_no_rebuild=True,
        tb_no_cleanup=True,
    )

    callback = agent_eval_suite.main.callback
    assert callback is not None
    callback(**options)

    result = json.loads(capsys.readouterr().out)
    assert result["cases"] == [{"case_id": "a"}]
    assert result["frameworks"]["tb_executable"] == "/bin/tb"
    assert result["inspect"] == {
        "returncode": 0,
        "stdout": "inspect ok",
        "stderr": "",
    }
    assert result["terminal_bench"]["stdout"] == "bench ok"


@pytest.mark.parametrize(
    ("stage", "expected"),
    [
        ("preflight", "framework preflight failed"),
        ("write", "failed to write Inspect task"),
    ],
)
def test_agent_eval_callback_reports_preflight_and_write_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    stage: str,
    expected: str,
) -> None:
    """Turn framework and task-publication exceptions into the CLI contract."""
    if stage == "preflight":
        monkeypatch.setattr(
            agent_eval_suite,
            "preflight_frameworks",
            lambda: (_ for _ in ()).throw(RuntimeError("framework missing")),
        )
    else:
        monkeypatch.setattr(
            agent_eval_suite,
            "write_inspect_task_file",
            lambda _: (_ for _ in ()).throw(OSError("read-only")),
        )
    options = _agent_options(tmp_path / "task.py")
    options["run_inspect"] = stage == "preflight"
    callback = agent_eval_suite.main.callback
    assert callback is not None

    with pytest.raises(SystemExit) as exc_info:
        callback(**options)

    assert exc_info.value.code == 3
    assert expected in capsys.readouterr().err


def test_agent_eval_callback_validates_requested_models_and_process_status(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Require a model for each framework and preserve its exit code."""
    task_path = tmp_path / "task.py"
    monkeypatch.setattr(
        agent_eval_suite,
        "preflight_frameworks",
        lambda: SimpleNamespace(
            inspect_ai="installed",
            terminal_bench="installed",
            tb_executable="/bin/tb",
        ),
    )
    monkeypatch.setattr(
        agent_eval_suite, "write_inspect_task_file", lambda _: task_path
    )
    options = _agent_options(task_path)
    options["run_inspect"] = True
    callback = agent_eval_suite.main.callback
    assert callback is not None
    with pytest.raises(SystemExit) as missing_inspect:
        callback(**options)
    assert missing_inspect.value.code == 2
    assert "requires --inspect-model" in capsys.readouterr().err

    options.update(run_inspect=False, run_terminal_bench=True)
    with pytest.raises(SystemExit) as missing_bench:
        callback(**options)
    assert missing_bench.value.code == 2
    assert "requires --tb-model" in capsys.readouterr().err

    options["tb_model"] = "provider/model"
    monkeypatch.setattr(
        agent_eval_suite,
        "run_terminal_bench_eval",
        lambda **_: SimpleNamespace(returncode=7, stdout="", stderr="failed"),
    )
    with pytest.raises(SystemExit) as failed_bench:
        callback(**options)
    output = json.loads(capsys.readouterr().out)
    assert failed_bench.value.code == 7
    assert output["terminal_bench"]["stderr"] == "failed"

    options.update(
        run_inspect=True,
        run_terminal_bench=False,
        inspect_model="provider/model",
    )
    monkeypatch.setattr(
        agent_eval_suite,
        "run_inspect_eval",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=5,
            stdout="inspect output",
            stderr="inspect failure",
        ),
    )
    with pytest.raises(SystemExit) as failed_inspect:
        callback(**options)
    inspect_output = json.loads(capsys.readouterr().out)
    assert failed_inspect.value.code == 5
    assert inspect_output["inspect"]["stderr"] == "inspect failure"


def test_collect_skills_callback_filters_and_publishes_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Publish only winning classes and retain the serialized skill contract."""

    def populate(index: SkillIndex, **_: object) -> None:
        index.add(
            Skill("writer", "Writer", class_="operation", source="project")
        )
        index.add(
            Skill("guide", "Guide", class_="documentation", source="project")
        )
        index._warnings.append("shadowed candidate")

    monkeypatch.setattr(collect_skills, "discover_all_skills", populate)
    destination = tmp_path / "inventory.json"
    callback = collect_skills.main.callback
    assert callback is not None
    callback(
        str(tmp_path),
        str(tmp_path),
        (),
        False,
        ("operation",),
        True,
        str(destination),
    )

    records = json.loads(destination.read_text(encoding="utf-8"))
    captured = capsys.readouterr()
    assert [item["name"] for item in records] == ["writer"]
    assert records[0]["selection"] == {}
    assert captured.out == ""
    assert "Warning: shadowed candidate" in captured.err
    assert list(tmp_path.glob(".*.tmp")) == []


def test_collect_skills_callback_stdout_and_fail_closed_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Keep stdout JSON-only and refuse failed or deferred discovery results."""
    callback = collect_skills.main.callback
    assert callback is not None
    monkeypatch.setattr(
        collect_skills, "discover_all_skills", lambda *_a, **_k: None
    )
    callback(str(tmp_path), str(tmp_path), (), False, (), False, None)
    assert json.loads(capsys.readouterr().out) == []

    def fail(*_: object, **__: object) -> None:
        raise OSError("unreadable root")

    monkeypatch.setattr(collect_skills, "discover_all_skills", fail)
    with pytest.raises(SystemExit) as error:
        callback(str(tmp_path), str(tmp_path), (), False, (), False, None)
    assert error.value.code == 1
    assert "unreadable root" in capsys.readouterr().err

    def deferred(index: SkillIndex, **_: object) -> None:
        object.__setattr__(index, "_discovery_errors", ["unresolved inventory"])

    monkeypatch.setattr(collect_skills, "discover_all_skills", deferred)
    with pytest.raises(SystemExit) as invalid_inventory:
        callback(str(tmp_path), str(tmp_path), (), False, (), False, None)
    assert invalid_inventory.value.code == 1
    assert "invalid inventory" in capsys.readouterr().err


def test_collect_skills_callback_cleans_temporary_output_after_write_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Report atomic-replacement errors and remove the unpublished temp file."""
    monkeypatch.setattr(
        collect_skills, "discover_all_skills", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(
        collect_skills.os,
        "replace",
        lambda *_args: (_ for _ in ()).throw(OSError("replace denied")),
    )
    destination = tmp_path / "inventory.json"
    callback = collect_skills.main.callback
    assert callback is not None
    with pytest.raises(SystemExit) as error:
        callback(
            str(tmp_path), str(tmp_path), (), False, (), False, str(destination)
        )
    assert error.value.code == 1
    assert "writing output: replace denied" in capsys.readouterr().err
    assert not destination.exists()
    assert list(tmp_path.glob(".*.tmp")) == []


def test_semantic_selection_callback_emits_result_and_maps_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Pass response settings through and translate evaluation errors."""
    fixture = {"inventory": [], "cases": []}
    monkeypatch.setattr(
        evaluate_semantic_selection, "load_fixture", lambda _: fixture
    )
    monkeypatch.setattr(
        evaluate_semantic_selection,
        "load_responses",
        lambda _: {"case": ["skill"]},
    )
    monkeypatch.setattr(
        evaluate_semantic_selection,
        "evaluate_fixture",
        lambda *_args, **kwargs: {"passed": True, "mode": kwargs["mode"]},
    )
    callback = evaluate_semantic_selection.main.callback
    assert callback is not None
    callback(
        tmp_path / "fixture.json",
        tmp_path,
        "configured-llm",
        tmp_path / "responses.json",
        "provider",
        "model",
        "host",
    )
    assert json.loads(capsys.readouterr().out) == {
        "passed": True,
        "mode": "configured-llm",
    }

    monkeypatch.setattr(
        evaluate_semantic_selection,
        "evaluate_fixture",
        lambda *_a, **_k: (_ for _ in ()).throw(EvaluationError("bad fixture")),
    )
    with pytest.raises(SystemExit) as exc_info:
        callback(
            tmp_path / "fixture.json",
            tmp_path,
            "deterministic",
            None,
            None,
            None,
            None,
        )
    assert exc_info.value.code == 2
    assert "bad fixture" in capsys.readouterr().err


def test_get_task_callback_reads_and_reports_invalid_input(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Return the selected task unchanged and map malformed input to exit 2."""
    task_file = tmp_path / "tasks.json"
    task_file.write_text('{"tasks":[{"taskId":"kept","context":"full"}]}')
    callback = get_task.main.callback
    assert callback is not None
    callback(task_file, "kept", None)
    assert json.loads(capsys.readouterr().out) == {
        "taskId": "kept",
        "context": "full",
    }

    task_file.write_text("{")
    with pytest.raises(SystemExit) as invalid_json:
        callback(task_file, "kept", None)
    assert invalid_json.value.code == 2
    assert "Error:" in capsys.readouterr().err

    with pytest.raises(SystemExit) as unreadable:
        callback(tmp_path / "absent.json", "kept", None)
    assert unreadable.value.code == 2
    assert "Error:" in capsys.readouterr().err


def test_select_task_rejects_ambiguous_roots_and_out_of_range_indices() -> None:
    """Require one selection mode and a canonical task-list object."""
    from lib.get_task.core import select_task

    with pytest.raises(ValueError, match="exactly one"):
        select_task({"tasks": []}, None, None)
    with pytest.raises(ValueError, match="exactly one"):
        select_task({"tasks": []}, "x", 0)
    with pytest.raises(ValueError, match="canonical task-packet"):
        select_task([], "x", None)
    with pytest.raises(ValueError, match="out of range"):
        select_task({"tasks": []}, None, 0)


def test_cli_modules_keep_domain_compatibility_exports() -> None:
    """Retain the established CLI import paths for extracted domain APIs."""
    from lib.get_task.core import select_task as select_task_api
    from lib.skill_validator import validate_skill_file

    assert get_task.select_task is select_task_api
    assert validate_skill_md.validate_skill_file is validate_skill_file


def test_resolve_script_root_callback_supports_text_and_json(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Present the core resolution result in both documented output formats."""
    monkeypatch.setattr(
        resolve_script_root,
        "resolve_script_root",
        lambda **_: (Path("/resolved/python"), "project-local"),
    )
    callback = resolve_script_root.main.callback
    assert callback is not None
    callback("python", None, "text")
    assert capsys.readouterr().out.strip() == "/resolved/python"
    callback("python", "/repo", "json")
    assert json.loads(capsys.readouterr().out) == {
        "path": "/resolved/python",
        "runtime": "python",
        "source": "project-local",
    }


def test_skill_validator_callback_exits_on_aggregate_check_results(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Serialize check results and set the documented aggregate status."""
    result = {"checks": [{"name": "frontmatter-valid", "passed": True}]}
    monkeypatch.setattr(skill_validator, "run_all", lambda _: result)
    callback = skill_validator.cli.callback
    assert callback is not None
    with pytest.raises(SystemExit) as passed:
        callback(str(tmp_path))
    assert passed.value.code == 0
    assert json.loads(capsys.readouterr().out) == result

    result["checks"][0]["passed"] = False
    with pytest.raises(SystemExit) as failed:
        callback(str(tmp_path))
    assert failed.value.code == 1
    assert json.loads(capsys.readouterr().out)["checks"][0]["passed"] is False


def _write_skill(path: Path, skill_class: str = "operation") -> Path:
    path.mkdir(parents=True, exist_ok=True)
    skill_file = path / "SKILL.md"
    profile = {
        "name": path.name,
        "description": "Use when validating the profile",
        "class": skill_class,
        "selection": {
            "role": "reference" if skill_class == "documentation" else "owner",
            "tags": {"actions": ["validate"]},
        },
    }
    skill_file.write_text(
        "---\n"
        + yaml.safe_dump(profile, sort_keys=False)
        + "---\n"
        + (
            "Reference notes.\n"
            if skill_class == "documentation"
            else "1. Validate.\n"
        ),
        encoding="utf-8",
    )
    return skill_file


def test_skill_markdown_callbacks_validate_one_or_many_profiles(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Return one record or a result list and fail if any profile is invalid."""
    valid = _write_skill(tmp_path / "valid-profile")
    result = validate_skill_md.validate_skill_file(valid)
    assert result == {"valid": True, "errors": []}

    invalid = _write_skill(tmp_path / "invalid-profile")
    invalid.write_text("body without frontmatter", encoding="utf-8")
    callback = validate_skill_md.main.callback
    assert callback is not None
    with pytest.raises(SystemExit) as failed:
        callback((str(valid), str(invalid)))
    assert failed.value.code == 1
    records = json.loads(capsys.readouterr().out)
    assert [record["valid"] for record in records] == [True, False]


def test_skill_markdown_file_validation_reports_frontmatter_and_body_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Report frontmatter and class-specific body errors."""
    from cli.validate_skill_md import _body_errors

    assert _body_errors(" ", "operation") == ["body must not be empty"]
    assert _body_errors("Reference", "operation") == [
        "active classes must define numbered execution steps"
    ]
    assert _body_errors("1. Steps are not allowed.", "documentation") == [
        "planning and documentation classes must not define execution steps"
    ]

    assert not validate_skill_md.validate_skill_file(tmp_path / "absent")[
        "valid"
    ]
    wrong_name = tmp_path / "other.md"
    wrong_name.write_text("---\n---\n", encoding="utf-8")
    wrong_name_result = validate_skill_md.validate_skill_file(wrong_name)
    assert "SKILL.md" in wrong_name_result["errors"][0]

    malformed = tmp_path / "broken" / "SKILL.md"
    malformed.parent.mkdir()
    malformed.write_text("---\nname: [bad\n---\n", encoding="utf-8")
    yaml_error = validate_skill_md.validate_skill_file(malformed)
    assert "YAML parse error" in yaml_error["errors"][0]

    closed = tmp_path / "closed" / "SKILL.md"
    closed.parent.mkdir()
    closed.write_text("---\nname: no-close\n", encoding="utf-8")
    assert (
        "closing delimiter"
        in validate_skill_md.validate_skill_file(closed)["errors"][0]
    )

    wrong_directory = _write_skill(
        tmp_path / "mismatch", skill_class="operation"
    )
    content = yaml.safe_load(wrong_directory.read_text().split("---\n")[1])
    content["name"] = "different-name"
    wrong_directory.write_text(
        "---\n" + yaml.safe_dump(content, sort_keys=False) + "---\n1. Done.\n",
        encoding="utf-8",
    )
    result = validate_skill_md.validate_skill_file(wrong_directory)
    assert any(
        "does not match directory" in error for error in result["errors"]
    )

    passive = _write_skill(
        tmp_path / "passive-profile", skill_class="documentation"
    )
    content = yaml.safe_load(passive.read_text().split("---\n")[1])
    content["selection"]["role"] = "owner"
    passive.write_text(
        "---\n"
        + yaml.safe_dump(content, sort_keys=False)
        + "---\nReference.\n",
        encoding="utf-8",
    )
    assert any(
        "selection.role reference" in error
        for error in validate_skill_md.validate_skill_file(passive)["errors"]
    )

    unreadable = tmp_path / "unreadable" / "SKILL.md"
    unreadable.parent.mkdir()
    unreadable.write_text("---\nname: readable\n---\n1. read\n")
    original_read_text = Path.read_text

    def fail_selected(
        path: Path,
        encoding: str | None = None,
        *,
        errors: str | None = None,
    ) -> str:
        if path == unreadable:
            raise OSError("read denied")
        return original_read_text(path, encoding=encoding, errors=errors)

    monkeypatch.setattr(Path, "read_text", fail_selected)
    read_error = validate_skill_md.validate_skill_file(unreadable)
    assert "Unable to read file" in read_error["errors"][0]


def test_skill_markdown_meta_callback_formats_each_validation_result(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Emit per-file text diagnostics or JSON and preserve invalid status."""
    valid = _write_skill(tmp_path / "valid-meta")
    invalid = _write_skill(tmp_path / "invalid-meta")
    invalid.write_text("---\nname: invalid\n---\n", encoding="utf-8")
    callback = validate_skill_meta.main.callback
    assert callback is not None
    callback((str(valid),), "text", True)
    output = capsys.readouterr()
    assert "VALID" in output.out
    assert "Validating:" in output.err

    with pytest.raises(SystemExit) as text_error:
        callback((str(invalid),), "text", False)
    assert text_error.value.code == 1
    assert "INVALID" in capsys.readouterr().out

    with pytest.raises(SystemExit) as failed:
        callback((str(valid), str(invalid)), "json", False)
    assert failed.value.code == 1
    result = json.loads(capsys.readouterr().out)
    assert [item["valid"] for item in result] == [True, False]
