"""Core helpers for the OpenCode agent evaluation suite.

The suite uses Inspect AI for local prompt/scorer evaluations and Terminal-Bench
for full terminal-sandbox benchmarks. Both frameworks are mandatory so missing
installs fail at preflight rather than silently reducing coverage.

Consumed by: agent-eval-suite.
"""

from __future__ import annotations

import importlib
import shutil
import subprocess
import textwrap
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

DEFAULT_INSPECT_TASK_PATH = Path("/tmp/opencode/opencode_agent_eval.py")


@dataclass(frozen=True)
class EvalCase:
    """One Inspect AI evaluation case."""

    case_id: str
    category: str
    prompt: str
    required_terms: tuple[str, ...]
    forbidden_terms: tuple[str, ...] = ()
    requires_json: bool = False


@dataclass(frozen=True)
class FrameworkStatus:
    """Installed framework status for Inspect AI and Terminal-Bench."""

    inspect_ai: str
    terminal_bench: str
    tb_executable: str


CASES: tuple[EvalCase, ...] = (
    EvalCase(
        case_id="past_breakdown_skill_creation",
        category="past_tasks",
        prompt=(
            "Decompose this request into worker packets: create an OpenCode skill "
            "named release-notes-writer that generates release notes from git "
            "history, including docs and validation. Return JSON only."
        ),
        required_terms=(
            "release-notes-writer",
            "skill-factory",
            "skills/release-notes-writer",
            "validation",
        ),
        forbidden_terms=("```", "skill-bash-writer"),
        requires_json=True,
    ),
    EvalCase(
        case_id="past_breakdown_node_script",
        category="past_tasks",
        prompt=(
            "Decompose this request into worker packets: create a TypeScript Node "
            "CLI script to validate task JSON files and add tests for it. Return "
            "JSON only."
        ),
        required_terms=(
            "skill-script-node-writer",
            "skill-script-node-test-writer",
            "validation",
            "tests",
        ),
        forbidden_terms=("```",),
        requires_json=True,
    ),
    EvalCase(
        case_id="write_code_minimal_patch",
        category="writing_code",
        prompt=(
            "Plan a minimal patch for a Python function that incorrectly returns "
            "None for empty input. Include implementation steps and verification."
        ),
        required_terms=("minimal", "test", "empty", "verification"),
    ),
    EvalCase(
        case_id="web_research_citations",
        category="web_research",
        prompt=(
            "Plan web research to compare two open-source LLM evaluation frameworks. "
            "Require source URLs, version/date checks, and a concise recommendation."
        ),
        required_terms=("source", "URL", "version", "recommendation"),
        forbidden_terms=("unsupported claim",),
    ),
    EvalCase(
        case_id="lint_format_cli",
        category="linting_formatting_cli_tools",
        prompt=(
            "Plan how to run linting, formatting, typechecking, and tests for a "
            "mixed TypeScript/Python repository. Include failure handling."
        ),
        required_terms=("lint", "format", "typecheck", "test", "failure"),
    ),
    EvalCase(
        case_id="root_cause_analysis",
        category="analysis",
        prompt=(
            "Analyze a bug report where an API returns HTTP 200 but downstream code "
            "sees empty content. Produce likely causes and verification steps."
        ),
        required_terms=("HTTP 200", "empty content", "logs", "reproduce"),
    ),
    EvalCase(
        case_id="codebase_research",
        category="codebase_research",
        prompt=(
            "Plan codebase research to identify where CLI entry points are registered, "
            "how tests are structured, and where shared validation logic lives."
        ),
        required_terms=("entry", "tests", "shared", "validation"),
    ),
    EvalCase(
        case_id="parse_data_schema",
        category="parsing_data",
        prompt=(
            "Design a parser for JSON evaluation results that groups model outcomes "
            "by category, distinguishes parse/schema/semantic failures, and emits a "
            "summary table."
        ),
        required_terms=("JSON", "parse", "schema", "semantic", "summary"),
    ),
    EvalCase(
        case_id="model_eval_json_only",
        category="ai_model_evaluation",
        prompt=(
            "Evaluate an AI model for strict JSON-only behavior. Ask it to return "
            "an object with keys summary, tasks, and verdict. The evaluation should "
            "fail outputs wrapped in markdown fences or explanatory prose. Return "
            "the evaluation plan as JSON only."
        ),
        required_terms=("summary", "tasks", "verdict", "markdown", "fail"),
        forbidden_terms=("```",),
        requires_json=True,
    ),
    EvalCase(
        case_id="model_eval_breakdown_schema",
        category="ai_model_evaluation",
        prompt=(
            "Design an AI model evaluation for the OpenCode breakdown-tasks schema. "
            "The scorer must check required fields purpose, context, filesToRead, "
            "filesToWrite, skills, executionInstructions, and expectedOutput. Return "
            "JSON only."
        ),
        required_terms=(
            "purpose",
            "context",
            "filesToRead",
            "filesToWrite",
            "executionInstructions",
            "expectedOutput",
        ),
        forbidden_terms=("```", "optionalVerification"),
        requires_json=True,
    ),
    EvalCase(
        case_id="model_eval_no_invented_skills",
        category="ai_model_evaluation",
        prompt=(
            "Create a model evaluation that detects invented skill names. The only "
            "available skills are generic-analysis, skill-script-node-writer, "
            "skill-script-node-test-writer, skill-factory, and skill-bash-conventions. "
            "The evaluation should fail outputs using unavailable skills such as "
            "skill-bash-writer or skill-react-component-development. Return JSON only."
        ),
        required_terms=(
            "available skills",
            "skill-factory",
            "skill-bash-writer",
            "fail",
        ),
        forbidden_terms=("```",),
        requires_json=True,
    ),
    EvalCase(
        case_id="model_eval_no_invented_paths",
        category="ai_model_evaluation",
        prompt=(
            "Design a model evaluation for requests where no repository file tree is "
            "provided. The evaluation must fail any response that invents paths like "
            "src/components/DarkModeToggle.jsx, README.md, or package.json unless the "
            "user explicitly supplied those paths. Return JSON only."
        ),
        required_terms=("filesToRead", "filesToWrite", "invent", "fail"),
        forbidden_terms=("```",),
        requires_json=True,
    ),
    EvalCase(
        case_id="model_eval_context_truncation",
        category="ai_model_evaluation",
        prompt=(
            "Plan an AI model evaluation for detecting context truncation and length "
            "finish reasons. The result should distinguish parse failures caused by "
            "invalid JSON from incomplete outputs caused by token limits. Return JSON "
            "only."
        ),
        required_terms=("finish", "length", "token", "parse", "incomplete"),
        forbidden_terms=("```",),
        requires_json=True,
    ),
    EvalCase(
        case_id="model_eval_repair_loop",
        category="ai_model_evaluation",
        prompt=(
            "Design a two-pass model evaluation with a repair loop. Pass one records "
            "raw output. Pass two tries safe repairs such as stripping markdown fences "
            "and revalidating JSON. The report must keep raw and repaired scores "
            "separate. Return JSON only."
        ),
        required_terms=("raw", "repaired", "markdown", "JSON", "separate"),
        forbidden_terms=("```",),
        requires_json=True,
    ),
    EvalCase(
        case_id="model_eval_terminal_bench_mapping",
        category="ai_model_evaluation",
        prompt=(
            "Map AI model capabilities to Terminal-Bench-style task categories for "
            "coding, data parsing, linting, codebase research, and web research. "
            "Include which categories require Docker sandbox execution versus simple "
            "Inspect scoring. Return JSON only."
        ),
        required_terms=("Terminal-Bench", "Docker", "Inspect", "coding", "parsing"),
        forbidden_terms=("```",),
        requires_json=True,
    ),
    EvalCase(
        case_id="model_eval_result_summary",
        category="ai_model_evaluation",
        prompt=(
            "Design a parser for AI model evaluation result files. It should group "
            "results by model and test category, count parse/schema/semantic failures, "
            "identify nondeterministic reruns, and emit a Markdown summary table. "
            "Return JSON only."
        ),
        required_terms=("model", "category", "parse", "schema", "semantic", "Markdown"),
        forbidden_terms=("```",),
        requires_json=True,
    ),
    EvalCase(
        case_id="worker_read_only_payload",
        category="worker_contract",
        prompt=(
            "Execute a read-only worker packet. Require a non-empty Deliverable, "
            "File Changes none, declared skill reconciliation, and verification "
            "evidence."
        ),
        required_terms=("Deliverable", "non-empty", "none", "verification"),
    ),
    EvalCase(
        case_id="worker_authorized_write",
        category="worker_contract",
        prompt=(
            "Evaluate a worker write packet: it may modify only FILES TO WRITE and "
            "must reconcile each actual write in File Changes."
        ),
        required_terms=("FILES TO WRITE", "File Changes", "reconcile", "authorized"),
    ),
    EvalCase(
        case_id="worker_no_op",
        category="worker_contract",
        prompt=(
            "Evaluate an already-compliant worker packet. It must return a non-empty "
            "payload and report the authorized target unchanged rather than inventing "
            "a modification."
        ),
        required_terms=("non-empty", "unchanged", "payload", "authorized"),
    ),
    EvalCase(
        case_id="worker_verification_payload",
        category="worker_contract",
        prompt=(
            "Evaluate a verification-only worker packet. It must return requested "
            "findings under Deliverable without requiring a file write."
        ),
        required_terms=("verification", "Deliverable", "findings", "file write"),
    ),
    EvalCase(
        case_id="worker_unavailable_skill",
        category="worker_contract",
        prompt=(
            "Evaluate a packet with an unavailable declared skill. It must return "
            "BLOCKED with blocker and unblock condition, not a success payload."
        ),
        required_terms=("BLOCKED", "blocker", "unblock", "skill"),
    ),
    EvalCase(
        case_id="worker_blocked_input",
        category="worker_contract",
        prompt=(
            "Evaluate a packet with unknown required input. It must block before side "
            "effects when the missing input prevents the deliverable."
        ),
        required_terms=(
            "BLOCKED",
            "before side effects",
            "missing input",
            "deliverable",
        ),
    ),
    EvalCase(
        case_id="worker_decomposition_false_completion",
        category="worker_contract",
        prompt=(
            "Evaluate decomposition where breakdown-tasks loads but no task path is "
            "produced. Reject COMPLETE or PARTIAL: loading a skill alone is not "
            "completion and Deliverable must be non-empty."
        ),
        required_terms=(
            "breakdown-tasks",
            "not completion",
            "Deliverable",
            "non-empty",
        ),
    ),
)


def list_cases() -> list[dict[str, Any]]:
    """Return serializable evaluation case metadata."""
    return [asdict(case) for case in CASES]


def preflight_frameworks() -> FrameworkStatus:
    """Verify Inspect AI, Terminal-Bench, and tb are installed."""
    inspect_ai = importlib.import_module("inspect_ai")
    terminal_bench = importlib.import_module("terminal_bench")
    tb_path = shutil.which("tb")
    if tb_path is None:
        msg = "Terminal-Bench CLI executable 'tb' was not found on PATH."
        raise RuntimeError(msg)
    return FrameworkStatus(
        inspect_ai=str(getattr(inspect_ai, "__version__", "installed")),
        terminal_bench=str(getattr(terminal_bench, "__version__", "installed")),
        tb_executable=tb_path,
    )


def write_inspect_task(path: Path = DEFAULT_INSPECT_TASK_PATH) -> Path:
    """Write an Inspect AI task module covering OpenCode workflow cases."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_inspect_task_source(), encoding="utf-8")
    return path


def run_inspect_eval(
    task_file: Path,
    model: str,
    log_dir: Path | None = None,
    limit: int | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run Inspect AI against the generated task file."""
    resolved_task_file = task_file.resolve()
    cmd = ["inspect", "eval", resolved_task_file.name, "--model", model]
    if log_dir is not None:
        cmd.extend(["--log-dir", str(log_dir)])
    if limit is not None:
        cmd.extend(["--limit", str(limit)])
    return subprocess.run(
        cmd,
        check=False,
        text=True,
        capture_output=True,
        cwd=resolved_task_file.parent,
    )


def run_terminal_bench(
    *,
    agent: str,
    agent_import_path: str | None = None,
    agent_kwargs: tuple[str, ...] = (),
    model: str,
    dataset: str,
    output_path: Path,
    task_ids: tuple[str, ...] = (),
    n_tasks: int | None = None,
    n_concurrent: int = 1,
    no_rebuild: bool = False,
    no_cleanup: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run Terminal-Bench with the requested dataset and agent."""
    cmd = [
        "tb",
        "run",
        "--model",
        model,
        "--dataset",
        dataset,
        "--output-path",
        str(output_path),
        "--n-concurrent",
        str(n_concurrent),
        "--no-upload-results",
    ]
    if agent_import_path is not None:
        cmd.extend(["--agent-import-path", agent_import_path])
    else:
        cmd.extend(["--agent", agent])
    for agent_kwarg in agent_kwargs:
        cmd.extend(["--agent-kwarg", agent_kwarg])
    for task_id in task_ids:
        cmd.extend(["--task-id", task_id])
    if n_tasks is not None:
        cmd.extend(["--n-tasks", str(n_tasks)])
    if no_rebuild:
        cmd.append("--no-rebuild")
    if no_cleanup:
        cmd.append("--no-cleanup")
    return subprocess.run(cmd, check=False, text=True, capture_output=True)


def _inspect_task_source() -> str:
    cases_literal = repr([asdict(case) for case in CASES])
    return (
        textwrap.dedent(
            f'''
            """Generated Inspect AI evals for OpenCode agent workflows."""

            from __future__ import annotations

            import json
            from typing import Any

            from inspect_ai import Task, task
            from inspect_ai.dataset import Sample
            from inspect_ai.scorer import (
                CORRECT,
                INCORRECT,
                Score,
                Target,
                accuracy,
                scorer,
                stderr,
            )
            from inspect_ai.solver import TaskState, generate


            CASES: list[dict[str, Any]] = {cases_literal}


            @scorer(metrics=[accuracy(), stderr()])
            def opencode_workflow_score():
                async def score(state: TaskState, target: Target) -> Score:
                    criteria = json.loads(target.text)
                    output = state.output.completion
                    errors: list[str] = []

                    if criteria.get("requires_json"):
                        try:
                            json.loads(output)
                        except json.JSONDecodeError as exc:
                            errors.append(f"invalid JSON: {{exc}}")

                    lowered = output.lower()
                    for term in criteria["required_terms"]:
                        if term.lower() not in lowered:
                            errors.append(f"missing required term: {{term}}")
                    for term in criteria["forbidden_terms"]:
                        if term.lower() in lowered:
                            errors.append(f"forbidden term present: {{term}}")

                    return Score(
                        value=INCORRECT if errors else CORRECT,
                        answer=output,
                        explanation=(
                            "; ".join(errors) if errors else "all checks passed"
                        ),
                        metadata={{
                            "case_id": criteria["case_id"],
                            "category": criteria["category"],
                        }},
                    )

                return score


            @task
            def opencode_agent_workflows() -> Task:
                samples = [
                    Sample(
                        id=case["case_id"],
                        input=case["prompt"],
                        target=json.dumps({{
                            "case_id": case["case_id"],
                            "category": case["category"],
                            "required_terms": list(case["required_terms"]),
                            "forbidden_terms": list(case["forbidden_terms"]),
                            "requires_json": case["requires_json"],
                        }}),
                    )
                    for case in CASES
                ]
                return Task(
                    dataset=samples,
                    solver=generate(),
                    scorer=opencode_workflow_score(),
                )
            '''
        ).strip()
        + "\n"
    )
