"""Direct-call coverage for atomic task-packet and task-rendering callbacks."""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any

import pytest

from cli import init_task_packet, render_task_markdown, validate_task_structure

pytestmark = pytest.mark.unit


def test_init_task_packet_publishes_valid_packet_without_replacing_files(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Publish the supplied slug atomically and retain collision protection."""
    data = {"slug": "preserved-slug", "tasks": []}
    monkeypatch.setattr(
        init_task_packet.click,
        "get_text_stream",
        lambda _: io.StringIO(json.dumps(data)),
    )
    monkeypatch.setattr(init_task_packet, "load_task_packet_schema", lambda: {})
    monkeypatch.setattr(
        init_task_packet, "validate_root", lambda *_: (True, [])
    )
    monkeypatch.setattr(
        init_task_packet.time,
        "time_ns",
        lambda: 1_700_000_000_000_000_000,
    )
    output_dir = tmp_path / "published"

    init_task_packet.main.callback(output_dir)

    destination = output_dir / "1700000000000-preserved-slug.json"
    assert capsys.readouterr().out.strip() == str(destination)
    assert json.loads(destination.read_text(encoding="utf-8")) == data
    assert list(output_dir.glob(".*.tmp")) == []

    monkeypatch.setattr(
        init_task_packet.click,
        "get_text_stream",
        lambda _: io.StringIO(json.dumps(data)),
    )
    with pytest.raises(SystemExit) as collision:
        init_task_packet.main.callback(output_dir)
    assert collision.value.code == 2
    assert "already exists" in capsys.readouterr().err
    assert json.loads(destination.read_text(encoding="utf-8")) == data


@pytest.mark.parametrize(
    ("stream", "schema_failure", "valid", "code", "message"),
    [
        ("{", False, True, 1, "not valid JSON"),
        ("[]", False, True, 1, "must be an object"),
        ('{"slug":"x"}', True, True, 2, "failed to load canonical"),
        ('{"slug":"x"}', False, False, 1, "canonical task-packet schema"),
    ],
)
def test_init_task_packet_rejects_input_and_schema_failures(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    stream: str,
    schema_failure: bool,
    valid: bool,
    code: int,
    message: str,
) -> None:
    """Return the prescribed error for malformed or invalid packet input."""
    monkeypatch.setattr(
        init_task_packet.click,
        "get_text_stream",
        lambda _: io.StringIO(stream),
    )
    monkeypatch.setattr(
        init_task_packet,
        "load_task_packet_schema",
        lambda: (_ for _ in ()).throw(OSError("schema unavailable"))
        if schema_failure
        else {},
    )
    monkeypatch.setattr(
        init_task_packet,
        "validate_root",
        lambda *_: (valid, ["bad root"]),
    )

    with pytest.raises(SystemExit) as exc_info:
        init_task_packet.main.callback(tmp_path / "unused")

    assert exc_info.value.code == code
    assert message in capsys.readouterr().err


def test_init_task_packet_handles_stdin_and_temporary_write_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Map input-stream and temporary-file failures to stable exit statuses."""
    monkeypatch.setattr(
        init_task_packet.click,
        "get_text_stream",
        lambda _: (_ for _ in ()).throw(OSError("closed stdin")),
    )
    with pytest.raises(SystemExit) as read_error:
        init_task_packet.main.callback(tmp_path)
    assert read_error.value.code == 1
    assert "reading stdin" in capsys.readouterr().err

    monkeypatch.setattr(
        init_task_packet.click,
        "get_text_stream",
        lambda _: io.StringIO('{"slug":"safe"}'),
    )
    monkeypatch.setattr(init_task_packet, "load_task_packet_schema", lambda: {})
    monkeypatch.setattr(
        init_task_packet, "validate_root", lambda *_: (True, [])
    )
    monkeypatch.setattr(
        init_task_packet.os,
        "fsync",
        lambda *_: (_ for _ in ()).throw(OSError("disk full")),
    )
    with pytest.raises(SystemExit) as write_error:
        init_task_packet.main.callback(tmp_path / "write-error")
    assert write_error.value.code == 2
    assert "writing output: disk full" in capsys.readouterr().err


def test_render_task_markdown_callback_reads_and_publishes_local_output(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Pass parsed task data to the renderer and print its local path."""
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "packet.json"
    source.write_text('{"summary":"kept"}', encoding="utf-8")
    output = tmp_path / "result.md"
    received: list[tuple[dict[str, Any], Path, bool]] = []

    def render(data: dict[str, Any], path: Path, *, overwrite: bool) -> Path:
        received.append((data, path, overwrite))
        path.write_text("# rendered\n", encoding="utf-8")
        return path

    monkeypatch.setattr(render_task_markdown, "render_task_markdown", render)
    render_task_markdown.main.callback(source, output, True)
    assert received == [({"summary": "kept"}, output, True)]
    assert capsys.readouterr().out.strip() == "result.md"
    assert output.read_text(encoding="utf-8") == "# rendered\n"


@pytest.mark.parametrize(
    "failure", ["outside", "non-object", "invalid-json", "renderer"]
)
def test_render_task_markdown_callback_reports_supported_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    failure: str,
) -> None:
    """Reject unsafe output paths and report input or rendering failures."""
    source = tmp_path / "packet.json"
    source.write_text("{}", encoding="utf-8")
    output = tmp_path / "result.md"
    if failure == "outside":
        other = tmp_path / "other"
        other.mkdir()
        monkeypatch.chdir(other)
    else:
        monkeypatch.chdir(tmp_path)
    if failure == "non-object":
        source.write_text("[]", encoding="utf-8")
    elif failure == "invalid-json":
        source.write_text("{", encoding="utf-8")
    elif failure == "renderer":
        monkeypatch.setattr(
            render_task_markdown,
            "render_task_markdown",
            lambda *_a, **_k: (_ for _ in ()).throw(ValueError("bad packet")),
        )

    with pytest.raises(SystemExit) as exc_info:
        render_task_markdown.main.callback(source, output, False)

    assert exc_info.value.code == 1
    assert "Error:" in capsys.readouterr().err


def test_validate_task_structure_callback_routes_all_input_modes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Validate file, stdin, and state data and preserve success diagnostics."""
    monkeypatch.setattr(validate_task_structure, "load_schema", lambda _: {})
    monkeypatch.setattr(
        validate_task_structure,
        "validate",
        lambda value, _: (
            (True, ["advisory"]) if value.get("advisory") else (True, [])
        ),
    )
    source = tmp_path / "packet.json"
    source.write_text('{"advisory":true}', encoding="utf-8")
    validate_task_structure.main.callback(
        str(source), False, None, False, "schema.json"
    )
    assert json.loads(capsys.readouterr().out) == {
        "valid": True,
        "diagnostics": ["advisory"],
    }

    monkeypatch.setattr(
        validate_task_structure.click,
        "get_text_stream",
        lambda _: io.StringIO('{"ok":true}'),
    )
    validate_task_structure.main.callback(
        None, True, None, False, "schema.json"
    )
    assert json.loads(capsys.readouterr().out) == {"valid": True}

    source.write_text('{"ok":true}', encoding="utf-8")
    validate_task_structure.main.callback(
        None, False, str(source), False, "schema.json"
    )
    assert json.loads(capsys.readouterr().out) == {"valid": True}


@pytest.mark.parametrize(
    ("file_path", "stdin", "state_file", "auto_fix", "message"),
    [
        ("file.json", True, None, False, "either a file path or --stdin"),
        ("file.json", False, "state.json", False, "mutually exclusive"),
        (None, False, None, False, "provide a file path"),
        (None, True, None, True, "requires --state-file"),
    ],
)
def test_validate_task_structure_callback_rejects_incompatible_modes(
    file_path: str | None,
    stdin: bool,
    state_file: str | None,
    auto_fix: bool,
    message: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Reject mutually exclusive or incomplete command modes before loading."""
    with pytest.raises(SystemExit) as exc_info:
        validate_task_structure.main.callback(
            file_path, stdin, state_file, auto_fix, "schema.json"
        )
    assert exc_info.value.code == 2
    assert message in capsys.readouterr().err


def test_validate_task_structure_callback_reports_failures_and_autofixes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Translate schema, file, parse, validation, and auto-fix outcomes."""
    source = tmp_path / "packet.json"
    source.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        validate_task_structure,
        "load_schema",
        lambda _: (_ for _ in ()).throw(ValueError("invalid schema")),
    )
    with pytest.raises(SystemExit) as schema_error:
        validate_task_structure.main.callback(
            str(source), False, None, False, "bad"
        )
    assert schema_error.value.code == 2
    assert "failed to load schema" in capsys.readouterr().err

    monkeypatch.setattr(validate_task_structure, "load_schema", lambda _: {})
    source.write_text("{", encoding="utf-8")
    with pytest.raises(SystemExit) as parse_error:
        validate_task_structure.main.callback(
            str(source), False, None, False, "schema"
        )
    assert parse_error.value.code == 2
    assert "invalid JSON input" in capsys.readouterr().err

    source.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        validate_task_structure,
        "validate",
        lambda *_: (_ for _ in ()).throw(RuntimeError("validator failed")),
    )
    with pytest.raises(SystemExit) as validation_error:
        validate_task_structure.main.callback(
            str(source), False, None, False, "schema"
        )
    assert validation_error.value.code == 2
    assert "validation error" in capsys.readouterr().err

    def fail_fix(*_: object):
        raise OSError("repair failed")

    monkeypatch.setattr(
        validate_task_structure, "auto_fix_task_structure", fail_fix
    )
    with pytest.raises(SystemExit) as fix_error:
        validate_task_structure.main.callback(
            None, False, str(source), True, "schema"
        )
    assert fix_error.value.code == 2
    assert "auto-fix failed" in capsys.readouterr().err

    monkeypatch.setattr(
        validate_task_structure,
        "auto_fix_task_structure",
        lambda *_: {"valid": False, "errors": ["cannot repair"]},
    )
    with pytest.raises(SystemExit) as invalid_fix:
        validate_task_structure.main.callback(
            None, False, str(source), True, "schema"
        )
    assert invalid_fix.value.code == 1
    assert json.loads(capsys.readouterr().out) == {
        "valid": False,
        "errors": ["cannot repair"],
    }

    monkeypatch.setattr(
        validate_task_structure,
        "auto_fix_task_structure",
        lambda *_: {"valid": True, "fixed": True},
    )
    validate_task_structure.main.callback(
        None, False, str(source), True, "schema"
    )
    assert json.loads(capsys.readouterr().out) == {"valid": True, "fixed": True}

    monkeypatch.setattr(
        validate_task_structure,
        "validate",
        lambda *_: (False, ["invalid packet"]),
    )
    with pytest.raises(SystemExit) as invalid_packet:
        validate_task_structure.main.callback(
            str(source), False, None, False, "schema"
        )
    assert invalid_packet.value.code == 1
    assert json.loads(capsys.readouterr().out) == {
        "valid": False,
        "errors": ["invalid packet"],
    }


def test_validate_task_structure_callback_reports_input_read_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Convert input read failures into the task CLI's file-error status."""
    source = tmp_path / "unreadable.json"
    source.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(validate_task_structure, "load_schema", lambda _: {})
    original_read_text = Path.read_text

    def fail_selected(path: Path, *args: object, **kwargs: object) -> str:
        if path == source:
            raise OSError("read denied")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fail_selected)
    with pytest.raises(SystemExit) as error:
        validate_task_structure.main.callback(
            str(source), False, None, False, "schema"
        )
    assert error.value.code == 2
    assert "failed to read input" in capsys.readouterr().err
