"""CLI publication regression tests for generate-task-json."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from zipfile import ZipFile

from click.testing import CliRunner

from cli.generate_task_json import main


def _packet() -> dict[str, object]:
    return {
        "summary": "CLI publication",
        "tasks": [
            {
                "purpose": "Publish the packet.",
                "context": "x" * 200,
                "filesToRead": [],
                "filesToWrite": [],
                "skills": ["demo"],
                "executionInstructions": [{"step": 1, "action": "Publish it."}],
                "expectedOutput": "A JSON packet.",
            }
        ],
    }


def _inventory(root: Path, *, path_root: Path | None = None) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    skill = (path_root or root) / "demo" / "SKILL.md"
    skill.parent.mkdir(parents=True, exist_ok=True)
    skill.write_text("# Demo\n", encoding="utf-8")
    inventory = root / "skills.json"
    inventory.write_text(
        json.dumps(
            [
                {
                    "name": "demo",
                    "description": "Use when testing packets",
                    "selection": {
                        "role": "owner",
                        "tags": {"actions": ["test"]},
                    },
                    "class": "operation",
                    "path": str(skill),
                    "source": "project",
                }
            ]
        ),
        encoding="utf-8",
    )
    return inventory


def _invoke(
    root: Path, inventory: Path, *output_args: str, project_root: Path | None = None
):
    return CliRunner().invoke(
        main,
        [
            "--skills-file",
            str(inventory),
            "--project-root",
            str(project_root or root),
            *output_args,
        ],
        input=json.dumps(_packet()),
    )


def test_cli_publishes_explicit_output_file(tmp_path: Path) -> None:
    inventory = _inventory(tmp_path)
    output = tmp_path / "packet.json"
    result = _invoke(tmp_path, inventory, "--output-file", str(output))
    assert result.exit_code == 0, result.output
    assert output.is_file()


def test_cli_publishes_output_directory_mode(tmp_path: Path) -> None:
    inventory = _inventory(tmp_path)
    output_dir = tmp_path / "tasks"
    result = _invoke(tmp_path, inventory, "--output-dir", str(output_dir))
    assert result.exit_code == 0, result.output
    assert list(output_dir.glob("*.json"))


def test_cli_rejects_existing_destination(tmp_path: Path) -> None:
    inventory = _inventory(tmp_path)
    output = tmp_path / "packet.json"
    output.write_text("existing", encoding="utf-8")
    result = _invoke(tmp_path, inventory, "--output-file", str(output))
    assert result.exit_code == 2
    assert "already exists" in result.output
    assert output.read_text(encoding="utf-8") == "existing"


def test_cli_rejects_inventory_path_outside_authorized_root(tmp_path: Path) -> None:
    inventory_root = tmp_path / "inventory"
    outside_root = tmp_path / "outside"
    inventory = _inventory(inventory_root, path_root=outside_root)
    result = _invoke(
        tmp_path,
        inventory,
        "--output-file",
        str(tmp_path / "packet.json"),
        project_root=inventory_root,
    )
    assert result.exit_code == 2
    assert "outside its source root" in result.output


def test_built_wheel_contains_task_packet_schema(tmp_path: Path) -> None:
    project = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(tmp_path)],
        cwd=project,
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    wheels = list(tmp_path.glob("*.whl"))
    assert len(wheels) == 1
    with ZipFile(wheels[0]) as wheel:
        assert (
            "lib/generate_task_json/assets/task-packet.schema.json"
            in wheel.namelist()
        )
