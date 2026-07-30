"""Select dynamic planning references and emit one bare JSON array.

The command intentionally owns discovery through ``select_planning_skills``;
callers never provide a skills inventory.  Diagnostics are published only to
the configured file and are content-free.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn

import click

from lib.generate_task_json.ollama_ranker import OllamaQwenScorer
from lib.generate_task_json.qwen_prompt import (
    QwenTokenBudget,
    render_planning_request,
)
from lib.generate_task_json.ranker import ScoreResult
from lib.generate_task_json.ranker_manifest import ManifestError, load_manifest
from lib.generate_task_json.ranking_diagnostics import (
    AtomicDiagnosticSink,
    PlanningSelectionDiagnosticRecord,
    canonical_hash,
    publish_planning_diagnostics,
)
from lib.select_planning_skills.core import select_planning_skills
from lib.select_planning_skills.policy import PlanningSelectionPolicy
from lib.select_planning_skills.prompt import (
    PLANNING_INSTRUCTION,
    PLANNING_PROMPT_VERSION,
    PLANNING_RENDER_VERSION,
)


class _DiagnosticScorer:
    """Capture derived ranking evidence without retaining source content."""

    def __init__(self, scorer: OllamaQwenScorer) -> None:
        self.scorer = scorer
        self.query_hash = ""
        self.inventory_hash = ""
        self.results: list[ScoreResult] = []
        self.documents: tuple[str, ...] = ()

    def score(self, query: str, documents: Sequence[str]) -> list[ScoreResult]:
        self.query_hash = canonical_hash(query)
        self.documents = tuple(documents)
        self.inventory_hash = canonical_hash(self.documents)
        self.results = self.scorer.score(query, documents)
        return self.results

    def diagnostic_identity(self) -> dict[str, str]:
        return dict(self.scorer.diagnostic_identity())


@click.command(name="select-planning-skills")
@click.option(
    "--project-root",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Project root used for dynamic skill discovery.",
)
@click.option(
    "--config-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="OpenCode configuration directory used for global skills.",
)
@click.option("--model-profile", type=click.Choice(("q8", "q4")), default="q8")
@click.option("--ollama-host", default="http://127.0.0.1:11434")
@click.option(
    "--diagnostics-file", type=click.Path(dir_okay=False, path_type=Path), default=None
)
@click.option(
    "--planning-policy",
    "--policy",
    required=True,
    help="Approved planning policy as a JSON object.",
)
def main(
    project_root: Path | None,
    config_dir: Path | None,
    model_profile: str,
    ollama_host: str,
    diagnostics_file: Path | None,
    planning_policy: str,
) -> None:
    """Read one complete task description from stdin and print selected names."""
    try:
        description = _read_description()
        policy = _read_policy(planning_policy)
        manifest = load_manifest(profile=model_profile)
        token_budget = QwenTokenBudget(
            manifest.tokenizer_path,
            expected_sha256=manifest.data["assets"]["tokenizer"]["sha256"],
            limit=manifest.num_ctx,
        )
        scorer = _DiagnosticScorer(
            OllamaQwenScorer(
                manifest,
                ollama_host,
                token_counter=token_budget.count,
                instruction=PLANNING_INSTRUCTION,
                prompt_identity=PLANNING_PROMPT_VERSION,
                render_identity=PLANNING_RENDER_VERSION,
                policy_identity=canonical_hash(policy),
            )
        )
        selected = select_planning_skills(
            description,
            scorer,
            project_root=project_root,
            config_dir=config_dir,
            policy=policy,
            token_budget=token_budget,
            preflight=token_budget.preflight,
        )
        if diagnostics_file is not None:
            _publish_diagnostics(
                diagnostics_file, description, policy, scorer, selected
            )
    except ManifestError as exc:
        _fail(exc, 3)
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError, TypeError) as exc:
        _fail(exc, 2)
    except (ImportError, ModuleNotFoundError) as exc:
        _fail(exc, 3)
    except (OSError, RuntimeError) as exc:
        _fail(exc, 1)
    click.echo(json.dumps(list(selected), ensure_ascii=True, separators=(",", ":")))


def _read_description() -> str:
    raw = click.get_binary_stream("stdin").read()
    description = raw.decode("utf-8")
    if not description.strip():
        raise ValueError("stdin must contain one non-empty task description")
    return description


def _read_policy(raw: str) -> PlanningSelectionPolicy:
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("planning policy must be a JSON object")
    allowed = {
        "absolute_inclusion_threshold",
        "minimum_cardinality",
        "max_cardinality",
        "decision_gate",
    }
    if set(value) != allowed:
        raise ValueError(f"planning policy must contain exactly {sorted(allowed)}")
    policy = PlanningSelectionPolicy(**value)
    if not policy.production_approved:
        raise ValueError("planning policy must be benchmark-approved")
    return policy


def _publish_diagnostics(
    path: Path,
    description: str,
    policy: PlanningSelectionPolicy,
    scorer: _DiagnosticScorer,
    selected: tuple[str, ...],
) -> None:
    identity = scorer.diagnostic_identity()
    record = PlanningSelectionDiagnosticRecord(
        model_hash=identity["model"],
        runtime_hash=identity["runtime"],
        tokenizer_hash=identity["tokenizer"],
        prompt_hash=identity["prompt"],
        renderer_hash=identity["render"],
        policy_hash=canonical_hash(policy),
        metadata_snapshot_hash=scorer.inventory_hash or canonical_hash(()),
        query_hash=scorer.query_hash
        or canonical_hash(render_planning_request(description)),
        candidate_scores=tuple(
            (_document_name(document, index), result.score)
            for index, (document, result) in enumerate(
                zip(scorer.documents, scorer.results, strict=False)
            )
        ),
        selected_names=selected,
        extra={"planning_render_version": PLANNING_RENDER_VERSION},
    )
    publish_planning_diagnostics(record, AtomicDiagnosticSink(path))


def _document_name(document: str, index: int) -> str:
    """Extract only the canonical identity from rendered candidate metadata."""
    prefix = "Skill name: "
    first_line = document.splitlines()[0] if document.splitlines() else ""
    return first_line.removeprefix(prefix) or f"candidate-{index}"


def _fail(error: Exception, code: int) -> NoReturn:
    click.echo(f"Error: {error}", err=True)
    raise SystemExit(code) from error


if __name__ == "__main__":  # pragma: no cover
    main()
