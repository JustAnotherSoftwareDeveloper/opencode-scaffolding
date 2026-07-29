"""CLI entry point for generate-task-json.

Reads a TaskDraftList JSON object from stdin and creates a valid,
skill-assigned BreakdownTasksOutput JSON object in the requested output directory.

Exit codes:
  0 — Output path written to stdout.
  1 — Manifest, model, transport, scoring, diagnostics, or output failed.
  2 — JSON, path, schema, inventory, token-budget, or argument error.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import click

from lib.generate_task_json.core import (
    GenerationValidationError,
    SummarySlugError,
    generate_task_json,
)
from lib.generate_task_json.ollama_ranker import OllamaQwenScorer
from lib.generate_task_json.qwen_prompt import (
    QwenPairPreflight,
    QwenPromptRenderer,
    QwenTokenBudget,
)
from lib.generate_task_json.ranker import RankingPolicy, SkillRanker
from lib.generate_task_json.ranker_manifest import ManifestError, load_manifest
from lib.generate_task_json.ranking_diagnostics import (
    AtomicDiagnosticSink,
)

_SCRIPT_PROJECT_ROOT = Path(__file__).resolve().parents[2]


@click.command(name="generate-task-json")
@click.option(
    "--skills-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path, readable=True),
    required=True,
    help="Frozen bare JSON array produced by collect-skills.",
)
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path, readable=True),
    default=None,
    help="Caller project root used to authorize project skill paths.",
)
@click.option(
    "--ranker-manifest",
    type=click.Path(exists=True, dir_okay=False, path_type=Path, readable=True),
    default=None,
    help="Checked ranker manifest (defaults to the packaged production manifest).",
)
@click.option(
    "--assignment-mode",
    type=click.Choice(("lexical", "shadow", "qwen")),
    default="qwen",
    show_default=True,
)
@click.option(
    "--model-profile", type=click.Choice(("q8", "q4")), default="q8", show_default=True
)
@click.option("--ollama-host", default="http://127.0.0.1:11434", show_default=True)
@click.option(
    "--diagnostics-file", type=click.Path(dir_okay=False, path_type=Path), default=None
)
@click.option(
    "--summary-slug",
    type=str,
    required=False,
    help="Kebab-case slug for the epoch-prefixed local .tasks output.",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, path_type=Path, resolve_path=True),
    required=False,
    help="Directory for the generated task JSON file.",
)
@click.option(
    "--output-file",
    type=click.Path(dir_okay=False, path_type=Path, resolve_path=True),
    required=False,
    help="Explicit JSON output file, mutually exclusive with legacy output options.",
)
def main(
    skills_file: Path,
    project_root: Path | None,
    ranker_manifest: Path | None,
    assignment_mode: str,
    model_profile: str,
    ollama_host: str,
    diagnostics_file: Path | None,
    summary_slug: str | None,
    output_dir: Path | None,
    output_file: Path | None,
) -> None:
    """Assign skills to stdin TaskDraftList JSON and print its local path."""
    try:
        _validate_destination_options(summary_slug, output_dir, output_file)
        if output_file is not None:
            _require_local_output(output_file)
        data = _read_stdin_json()
        skills = _read_skills_file(skills_file)
        ranker_factory = None
        diagnostic_sink = None
        pair_preflight = None
        caller_root = (project_root or _caller_working_directory()).resolve()
        if assignment_mode in {"qwen", "shadow"}:
            if assignment_mode == "shadow" and diagnostics_file is None:
                raise ValueError("shadow mode requires --diagnostics-file")
            manifest = load_manifest(ranker_manifest, model_profile)
            budget = QwenTokenBudget(
                manifest.tokenizer_path,
                expected_sha256=manifest.data["assets"]["tokenizer"]["sha256"],
                limit=manifest.num_ctx,
            )
            renderer = QwenPromptRenderer(
                budget,
                instruction=manifest.data["prompt"]["instruction"],
            )
            pair_preflight = QwenPairPreflight(renderer)

            # Core validates and freezes the inventory before calling this factory.
            def make_ranker(_candidates):
                scorer = OllamaQwenScorer(
                    manifest,
                    ollama_host,
                    token_counter=budget.count,
                )
                return SkillRanker(scorer, RankingPolicy.from_manifest(manifest.data))

            ranker_factory = make_ranker
            if diagnostics_file is not None:
                diagnostic_sink = AtomicDiagnosticSink(diagnostics_file)
        output_path = generate_task_json(
            data,
            summary_slug,
            output_dir=output_dir,
            output_file=output_file,
            inventory_project_root=caller_root,
            skills_index=skills,
            assignment_mode=assignment_mode,
            ranker_factory=ranker_factory,
            diagnostic_sink=diagnostic_sink,
            pair_preflight=pair_preflight,
        )
    except ManifestError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc
    except RuntimeError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc
    except (
        GenerationValidationError,
        SummarySlugError,
        json.JSONDecodeError,
        ValueError,
    ) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2) from exc
    except OSError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc
    click.echo(str(_relative_output_path(output_path)))


def _require_local_output(path: Path) -> None:
    """Reject an explicit output path outside the current working directory."""
    if not path.is_relative_to(_caller_working_directory()):
        raise ValueError("--output-file must be within the current working directory")


def _caller_working_directory() -> Path:
    """Return the caller directory preserved in PWD by ``uv --directory``."""
    current_directory = Path.cwd().resolve()
    if current_directory != _SCRIPT_PROJECT_ROOT:
        return current_directory
    return Path(os.environ.get("PWD", current_directory)).resolve()


def _relative_output_path(output_path: Path) -> Path:
    """Render output relative to the caller directory when possible."""
    caller_directory = _caller_working_directory()
    if output_path.is_relative_to(caller_directory):
        return output_path.relative_to(caller_directory)
    return output_path.relative_to(output_path.parent)


def _validate_destination_options(
    summary_slug: str | None,
    output_dir: Path | None,
    output_file: Path | None,
) -> None:
    """Require either an output directory (slug may be derived) or an explicit file."""
    legacy = summary_slug is not None or output_dir is not None
    if output_file is not None and legacy:
        raise ValueError(
            "--output-file is mutually exclusive with legacy output options"
        )
    if output_file is None and output_dir is None:
        raise ValueError(
            "provide --output-file or --output-dir (--summary-slug is optional)"
        )


def _read_stdin_json() -> dict[str, Any]:
    """Read and parse one JSON object from standard input."""
    data = json.loads(click.get_text_stream("stdin").read())
    if not isinstance(data, dict):
        raise ValueError("stdin JSON must be an object")
    return data


def _read_skills_file(path: Path) -> list[dict[str, Any]]:
    """Read only the collector's frozen, bare array; never discover from CWD."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError("--skills-file must contain a bare JSON array")
    if any(not isinstance(item, dict) for item in value):
        raise ValueError("--skills-file entries must be objects")
    return value


if __name__ == "__main__":  # pragma: no cover
    main()
