"""Direct-call coverage for atomic task-packet and task-rendering callbacks."""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any

import pytest

from cli import init_task_packet, render_task_markdown, validate_task_structure
from lib.task_packet import (
    InvalidTaskPacketError,
    TaskPacketSchemaError,
    initialize_task_packet,
)
from lib.task_packet import initialization as packet_initialization

pytestmark = pytest.mark.unit


def test_initialize_task_packet_publishes_valid_packet_and_rejects_collision(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Publish a valid packet atomically and preserve collision protection."""
    data = {"slug": "preserved-slug", "tasks": []}
    monkeypatch.setattr(
        packet_initialization, "load_task_packet_schema", lambda: {}
    )
    monkeypatch.setattr(
        packet_initialization, "validate_root", lambda *_: (True, [])
    )
    monkeypatch.setattr(
        packet_initialization.time, "time_ns", lambda: 1_700_000_000_000_000_000
    )
    output_dir = tmp_path / "published"

    destination = initialize_task_packet(data, output_dir)

    assert destination == output_dir / "1700000000000-preserved-slug.json"
    assert json.loads(destination.read_text(encoding="utf-8")) == data
    assert list(output_dir.glob(".*.tmp")) == []

    with pytest.raises(FileExistsError, match="already exists"):
        initialize_task_packet(data, output_dir)
    assert json.loads(destination.read_text(encoding="utf-8")) == data
    assert list(output_dir.glob(".*.tmp")) == []


def test_initialize_task_packet_rejects_invalid_packet_without_publication(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Reject invalid canonical data before creating publication files."""
    monkeypatch.setattr(
        packet_initialization, "load_task_packet_schema", lambda: {}
    )
    monkeypatch.setattr(
        packet_initialization,
        "validate_root",
        lambda *_: (False, ["bad root"]),
    )
    output_dir = tmp_path / "not-published"

    with pytest.raises(InvalidTaskPacketError, match="bad root"):
        initialize_task_packet({"slug": "safe", "tasks": []}, output_dir)

    assert not output_dir.exists()
    assert list(tmp_path.iterdir()) == []


def test_initialize_task_packet_wraps_schema_load_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Expose schema loading failures through the domain error contract."""
    monkeypatch.setattr(
        packet_initialization,
        "load_task_packet_schema",
        lambda: (_ for _ in ()).throw(OSError("schema unavailable")),
    )

    with pytest.raises(TaskPacketSchemaError, match="schema unavailable"):
        initialize_task_packet({"slug": "safe", "tasks": []}, tmp_path / "out")

    assert not (tmp_path / "out").exists()


def test_initialize_task_packet_cleans_temporary_file_after_write_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Remove partial output after an atomic-write filesystem failure."""
    data = {"slug": "safe", "tasks": []}
    monkeypatch.setattr(
        packet_initialization, "load_task_packet_schema", lambda: {}
    )
    monkeypatch.setattr(
        packet_initialization, "validate_root", lambda *_: (True, [])
    )
    monkeypatch.setattr(
        packet_initialization.time,
        "time_ns",
        lambda: 1_700_000_000_000_000_000,
    )
    monkeypatch.setattr(
        packet_initialization.os,
        "fsync",
        lambda *_: (_ for _ in ()).throw(OSError("disk full")),
    )
    output_dir = tmp_path / "write-error"

    with pytest.raises(OSError, match="disk full"):
        initialize_task_packet(data, output_dir)

    assert output_dir.is_dir()
    assert list(output_dir.iterdir()) == []


def test_init_task_packet_adapter_publishes_domain_result(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Pass parsed input to the domain operation and print its returned path."""
    packet = {"slug": "safe"}
    destination = Path("output") / "result.json"
    received: list[tuple[object, Path]] = []

    monkeypatch.setattr(
        init_task_packet.click,
        "get_text_stream",
        lambda _: io.StringIO(json.dumps(packet)),
    )

    def initialize(data: object, output_dir: Path) -> Path:
        received.append((data, output_dir))
        return destination

    monkeypatch.setattr(init_task_packet, "initialize_task_packet", initialize)
    callback = init_task_packet.main.callback
    assert callback is not None
    callback(Path("output"))

    assert received == [(packet, Path("output"))]
    assert capsys.readouterr().out.strip() == str(destination)


def test_init_task_packet_adapter_maps_stdin_read_failure(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Map an input stream read failure to the environment exit status."""

    class FailingStream:
        """A stdin fake that fails when the adapter reads it."""

        def read(self) -> str:
            raise OSError("closed stdin")

    monkeypatch.setattr(
        init_task_packet.click, "get_text_stream", lambda _: FailingStream()
    )

    callback = init_task_packet.main.callback
    assert callback is not None
    with pytest.raises(SystemExit) as error:
        callback(Path("output"))

    captured = capsys.readouterr()
    assert error.value.code == 3
    assert "Error: reading stdin: closed stdin" in captured.err
    assert captured.out == ""


@pytest.mark.parametrize(
    ("raw", "failure", "code", "message"),
    [
        ("{", None, 2, "not valid JSON"),
        ("[]", None, 2, "must be an object"),
        (
            '{"slug":"x"}',
            InvalidTaskPacketError("bad packet"),
            2,
            "bad packet",
        ),
        (
            '{"slug":"x"}',
            TaskPacketSchemaError("schema unavailable"),
            3,
            "schema unavailable",
        ),
        ('{"slug":"x"}', OSError("write denied"), 3, "write denied"),
    ],
)
def test_init_task_packet_adapter_maps_input_and_domain_errors(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    raw: str,
    failure: Exception | None,
    code: int,
    message: str,
) -> None:
    """Keep the CLI adapter's bad-input and environment statuses distinct."""
    monkeypatch.setattr(
        init_task_packet.click, "get_text_stream", lambda _: io.StringIO(raw)
    )
    monkeypatch.setattr(
        init_task_packet,
        "initialize_task_packet",
        lambda *_: (
            (_ for _ in ()).throw(failure) if failure else Path("result.json")
        ),
    )
    callback = init_task_packet.main.callback
    assert callback is not None

    if code == 0:
        callback(Path("output"))
        assert capsys.readouterr().out.strip() == "result.json"
        return

    with pytest.raises(SystemExit) as error:
        callback(Path("output"))

    captured = capsys.readouterr()
    assert error.value.code == code
    assert message in captured.err
    assert captured.out == ""


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
    callback = render_task_markdown.main.callback
    assert callback is not None
    callback(source, output, True)
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

    callback = render_task_markdown.main.callback
    assert callback is not None
    with pytest.raises(SystemExit) as exc_info:
        callback(source, output, False)

    assert exc_info.value.code == 2
    assert "Error:" in capsys.readouterr().err


def test_render_task_markdown_callback_maps_filesystem_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Report renderer filesystem failures with the environment status."""
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "packet.json"
    source.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        render_task_markdown,
        "render_task_markdown",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("disk full")),
    )

    callback = render_task_markdown.main.callback
    assert callback is not None
    with pytest.raises(SystemExit) as error:
        callback(source, tmp_path / "result.md", False)

    captured = capsys.readouterr()
    assert error.value.code == 3
    assert "Error: disk full" in captured.err
    assert captured.out == ""


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
    callback = validate_task_structure.main.callback
    assert callback is not None
    callback(str(source), False, None, False, "schema.json")
    assert json.loads(capsys.readouterr().out) == {
        "valid": True,
        "diagnostics": ["advisory"],
    }

    monkeypatch.setattr(
        validate_task_structure.click,
        "get_text_stream",
        lambda _: io.StringIO('{"ok":true}'),
    )
    callback(None, True, None, False, "schema.json")
    assert json.loads(capsys.readouterr().out) == {"valid": True}

    source.write_text('{"ok":true}', encoding="utf-8")
    callback(None, False, str(source), False, "schema.json")
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
    callback = validate_task_structure.main.callback
    assert callback is not None
    with pytest.raises(SystemExit) as exc_info:
        callback(file_path, stdin, state_file, auto_fix, "schema.json")
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
    callback = validate_task_structure.main.callback
    assert callback is not None
    with pytest.raises(SystemExit) as schema_error:
        callback(str(source), False, None, False, "bad")
    assert schema_error.value.code == 3
    assert "failed to load schema" in capsys.readouterr().err

    monkeypatch.setattr(validate_task_structure, "load_schema", lambda _: {})
    source.write_text("{", encoding="utf-8")
    with pytest.raises(SystemExit) as parse_error:
        callback(str(source), False, None, False, "schema")
    assert parse_error.value.code == 2
    assert "invalid JSON input" in capsys.readouterr().err

    source.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        validate_task_structure,
        "validate",
        lambda *_: (_ for _ in ()).throw(RuntimeError("validator failed")),
    )
    with pytest.raises(SystemExit) as validation_error:
        callback(str(source), False, None, False, "schema")
    assert validation_error.value.code == 2
    assert "validation error" in capsys.readouterr().err

    def fail_fix(*_: object):
        raise OSError("repair failed")

    monkeypatch.setattr(
        validate_task_structure, "auto_fix_task_structure", fail_fix
    )
    with pytest.raises(SystemExit) as fix_error:
        callback(None, False, str(source), True, "schema")
    assert fix_error.value.code == 2
    assert "auto-fix failed" in capsys.readouterr().err

    monkeypatch.setattr(
        validate_task_structure,
        "auto_fix_task_structure",
        lambda *_: {"valid": False, "errors": ["cannot repair"]},
    )
    with pytest.raises(SystemExit) as invalid_fix:
        callback(None, False, str(source), True, "schema")
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
    callback(None, False, str(source), True, "schema")
    assert json.loads(capsys.readouterr().out) == {"valid": True, "fixed": True}

    monkeypatch.setattr(
        validate_task_structure,
        "validate",
        lambda *_: (False, ["invalid packet"]),
    )
    with pytest.raises(SystemExit) as invalid_packet:
        callback(str(source), False, None, False, "schema")
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

    def fail_selected(
        path: Path,
        encoding: str | None = None,
        *,
        errors: str | None = None,
    ) -> str:
        if path == source:
            raise OSError("read denied")
        return original_read_text(path, encoding=encoding, errors=errors)

    monkeypatch.setattr(Path, "read_text", fail_selected)
    callback = validate_task_structure.main.callback
    assert callback is not None
    with pytest.raises(SystemExit) as error:
        callback(str(source), False, None, False, "schema")
    assert error.value.code == 3
    assert "failed to read input" in capsys.readouterr().err
