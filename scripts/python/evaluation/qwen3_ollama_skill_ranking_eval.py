"""Run an opt-in native evaluation through the production Qwen ranker."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import subprocess
import time
from pathlib import Path
from typing import Any

from lib.generate_task_json.ollama_ranker import OllamaQwenScorer
from lib.generate_task_json.qwen_prompt import (
    QwenPairPreflight,
    QwenPromptRenderer,
    QwenTokenBudget,
)
from lib.generate_task_json.ranker import RankingPolicy, SkillCandidate, SkillRanker
from lib.generate_task_json.ranker_manifest import load_manifest
from lib.generate_task_json.ranking_diagnostics import canonical_hash

VERSION = "2026-07-29.4"
CASES = [
    (
        "analysis",
        "Analyze the failure and recommend next actions.",
        "generic-analysis",
        ["generic-analysis"],
    ),
    (
        "proposal",
        "Create an evidence-based decision proposal.",
        "proposal",
        ["proposal"],
    ),
    (
        "plan",
        "Create an executable source-document plan workspace.",
        "plan",
        ["plan"],
    ),
    (
        "python-writer",
        "Implement a deterministic Python Click CLI.",
        "skill-script-python-writer",
        ["skill-script-python-writer"],
    ),
    (
        "python-tests",
        "Write pytest coverage for an existing Python CLI.",
        "skill-script-python-test-writer",
        ["skill-script-python-test-writer"],
    ),
    (
        "node-writer",
        "Implement a deterministic TypeScript command-line script.",
        "skill-script-node-writer",
        ["skill-script-node-writer", "skill-node-script-conventions"],
    ),
    (
        "node-tests",
        "Write Bun tests for an existing TypeScript CLI.",
        "skill-script-node-test-writer",
        ["skill-script-node-test-writer", "skill-node-script-conventions"],
    ),
    (
        "bash-writer",
        "Implement a deterministic Bash CLI.",
        "skill-script-bash-writer",
        ["skill-script-bash-writer", "skill-bash-conventions"],
    ),
    (
        "bash-tests",
        "Write bats-core tests for an existing Bash script.",
        "skill-script-bash-test-writer",
        [
            "skill-script-bash-test-writer",
            "skill-script-bash-writer",
            "skill-bash-conventions",
        ],
    ),
    (
        "skill-factory",
        "Create a complete new OpenCode skill.",
        "skill-factory",
        ["skill-factory", "skill-authoring-guide", "skill-template-library"],
    ),
    (
        "worker-engine-reference",
        "Explain packet execution behavior in OpenCode worker agents.",
        "customize-opencode",
        ["customize-opencode"],
    ),
    (
        "orchestration-reference",
        "Design a delegated worker fan-out and collation pattern.",
        "skill-orchestration-reference",
        ["skill-orchestration-reference", "customize-opencode"],
    ),
    ("no-specialist", "Rename one local variable for clarity.", None, []),
]


def collect_skills(root: Path, config_dir: Path) -> list[dict[str, Any]]:
    command = [
        "uv",
        "run",
        "--directory",
        str(config_dir / "scripts/python"),
        "collect-skills",
        "--project-root",
        str(root),
        "--config-dir",
        str(config_dir),
        "--class",
        "operation",
        "--class",
        "documentation",
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    value = json.loads(result.stdout)
    if not isinstance(value, list):
        raise ValueError("collect-skills did not return an array")
    return value


def task(case: tuple[str, str, str | None, list[str]]) -> dict[str, Any]:
    identifier, purpose, _primary, _expected = case
    files_to_write = (
        ["skills/new-skill/SKILL.md"] if identifier == "skill-factory" else []
    )
    return {
        "id": identifier,
        "purpose": purpose,
        "context": (
            "Use the repository procedures needed to complete the requested "
            "deliverable with deterministic validation and bounded changes."
        ),
        "filesToRead": [],
        "filesToWrite": files_to_write,
        "executionInstructions": [{"step": 1, "action": purpose}],
        "verification": ["Validate the completed artifact."],
        "expectedOutput": purpose,
    }


def _percentile(values: list[float], percentile: float) -> float:
    index = max(0, math.ceil(percentile * len(values)) - 1)
    return sorted(values)[index]


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    root = args.project_root.resolve()
    config_dir = args.config_dir.resolve()
    inventory = collect_skills(root, config_dir)
    source_roots = {"project": (root,), "global": (config_dir,)}
    candidates = tuple(
        SkillCandidate.from_metadata(
            item,
            original_index=index,
            approved_source_roots=source_roots,
        )
        for index, item in enumerate(inventory)
    )
    manifest = load_manifest(args.ranker_manifest, args.model_profile)
    budget = QwenTokenBudget(
        manifest.tokenizer_path,
        expected_sha256=manifest.data["assets"]["tokenizer"]["sha256"],
        limit=manifest.num_ctx,
    )
    drafts = [task(case) for case in CASES]
    QwenPairPreflight(
        QwenPromptRenderer(
            budget,
            instruction=manifest.data["prompt"]["instruction"],
        )
    )(drafts, candidates)
    scorer = OllamaQwenScorer(
        manifest,
        args.host,
        timeout=args.timeout,
        token_counter=budget.count,
    )
    ranker = SkillRanker(scorer, RankingPolicy.from_manifest(manifest.data))
    fixture_results: list[dict[str, Any]] = []
    complete_seconds: list[float] = []
    request_seconds: list[float] = []
    clipped_count = 0
    load_seconds: list[float] = []
    for case, draft in zip(CASES, drafts, strict=True):
        started = time.monotonic()
        result = ranker.rank(draft, candidates)
        complete_seconds.append(time.monotonic() - started)
        request_seconds.extend(scorer.last_request_seconds)
        load_seconds.extend(scorer.last_load_seconds)
        clipped_count += sum(bool(value) for value in scorer.last_clipped_labels)
        fixture_results.append(
            {
                "id": case[0],
                "primary": case[2],
                "expected": case[3],
                "selected": list(result.names),
                "primary_hit": case[2] is None or result.names[0] == case[2],
                "scores": [
                    list(value) for value in result.diagnostics.candidate_scores
                ],
                "prompt_hashes": list(result.diagnostics.pair_prompt_hashes),
                "token_counts": list(result.diagnostics.token_counts),
            }
        )
    positive = [row for row in fixture_results if row["primary"]]
    selected = [set(row["selected"]) for row in positive]
    expected = [set(row["expected"]) for row in positive]
    true_positive = sum(
        len(actual & target) for actual, target in zip(selected, expected, strict=True)
    )
    false_positive = sum(
        len(actual - target) for actual, target in zip(selected, expected, strict=True)
    )
    false_negative = sum(
        len(target - actual) for actual, target in zip(selected, expected, strict=True)
    )
    return {
        "evaluation_version": VERSION,
        "profile": manifest.profile,
        "model": manifest.model,
        "manifest_hash": canonical_hash(manifest.data),
        "runtime_version": scorer.runtime_version,
        "tokenizer_hash": budget.tokenizer_digest,
        "prompt_version": manifest.data["prompt"]["prompt_version"],
        "render_version": manifest.data["prompt"]["render_version"],
        "inventory_hash": canonical_hash(inventory),
        "skill_count": len(candidates),
        "fixture_count": len(CASES),
        "top1_accuracy": sum(row["primary_hit"] for row in positive) / len(positive),
        "selection_policy_0_8": {
            "precision": true_positive / (true_positive + false_positive),
            "recall": true_positive / (true_positive + false_negative),
            "exact_set_accuracy": sum(
                actual == target
                for actual, target in zip(selected, expected, strict=True)
            )
            / len(positive),
        },
        "clipped_label_request_count": clipped_count,
        "score_request_count": len(request_seconds),
        "warm_request_seconds": {
            "mean": statistics.mean(request_seconds),
            "p95": _percentile(request_seconds, 0.95),
        },
        "complete_task_seconds": {
            "mean": statistics.mean(complete_seconds),
            "p95": _percentile(complete_seconds, 0.95),
        },
        "cold_load_seconds": {"max": max(load_seconds)},
        "independent_vram": args.independent_vram
        or {
            "status": "blocked",
            "reason": "NVML unavailable; Ollama allocation is not independent.",
        },
        "fixtures": fixture_results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--config-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model-profile", choices=("q8", "q4"), default="q8")
    parser.add_argument("--ranker-manifest", type=Path)
    parser.add_argument("--host", default="http://127.0.0.1:11434")
    parser.add_argument("--timeout", type=float, default=600)
    parser.add_argument("--independent-vram", type=json.loads, default=None)
    args = parser.parse_args()
    report = evaluate(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {key: value for key, value in report.items() if key != "fixtures"},
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
