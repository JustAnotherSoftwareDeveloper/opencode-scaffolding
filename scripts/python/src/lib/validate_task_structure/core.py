"""Task structure validation against the task-packet JSON Schema.

Validates task objects for required keys, length constraints,
step numbering, file array rules, and type correctness.
Consumed by: validate-task-structure.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import jsonschema


def _validate_file_array(arr: list[Any], path: str, label: str) -> list[str]:
    """Validate a file path array: all strings, no duplicates, no empty strings."""
    errors: list[str] = []

    seen: set[str] = set()
    for i, item in enumerate(arr):
        if not isinstance(item, str):
            errors.append(
                f"{path}.{label}[{i}]: expected string, got {type(item).__name__}"
            )
        elif item == "":
            errors.append(f"{path}.{label}[{i}]: empty string not allowed")
        elif re.search(r"<[^<>]+>|\$\{[^{}]+\}|\{\{[^{}]+\}\}", item):
            errors.append(
                f"{path}.{label}[{i}]: placeholder path not allowed: {item!r}"
            )
        elif item in seen:
            errors.append(f"{path}.{label}: duplicate entry: {item!r}")
        seen.add(item)
    return errors


def _validate_execution_steps(steps: list[dict[str, Any]], path: str) -> list[str]:
    """Validate execution instruction steps are sequential starting at 1."""
    errors: list[str] = []
    for i, step in enumerate(steps, start=1):
        step_num = step.get("step")
        if step_num != i:
            errors.append(
                f"{path}.executionInstructions[{i - 1}]: "
                f"expected step {i}, got {step_num}"
            )
    return errors


def _diagnostic(level: str, criterion: str, path: str, message: str) -> str:
    """Format a staged, actionable publication-gate diagnostic."""
    return f"{level} [{criterion}] {path}: {message}"


def _root_schema_errors(
    packet: Any, schema: dict[str, Any]
) -> list[jsonschema.ValidationError]:
    """Return deterministic canonical-root schema errors for *packet*."""
    validator = jsonschema.Draft7Validator(
        schema, format_checker=jsonschema.Draft7Validator.FORMAT_CHECKER
    )
    return sorted(
        validator.iter_errors(packet),
        key=lambda error: (
            tuple(str(part) for part in error.absolute_path),
            error.message,
        ),
    )


def validate_root(packet: Any, schema: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a complete task-packet root against its canonical schema.

    This validates the enclosing object, including its required ``summary`` and
    immutable ``slug`` identity, and rejects extra roots.
    """
    errors = _root_schema_errors(packet, schema)
    if errors:
        return False, _format_root_errors(errors)
    return_errors = _validate_boundary_review(packet)
    return not return_errors, return_errors


def _validate_boundary_review(packet: dict[str, Any]) -> list[str]:
    """Check cross-field consistency in a schema-valid boundary-review record.

    This is deliberately limited to references and mutually exclusive record
    shapes.  It neither interprets prose nor determines whether a task is
    semantically atomic; that request-aware decision remains with the delegator.
    """
    diagnostics: list[str] = []
    tasks = packet["tasks"]
    assert isinstance(tasks, list)
    task_ids = {task["taskId"] for task in tasks if isinstance(task, dict)}
    review = packet["boundaryReview"]
    assert isinstance(review, dict)
    task_reviews = review["taskReviews"]
    assert isinstance(task_reviews, dict)

    reviewed_ids = set(task_reviews)
    for task_id in sorted(task_ids - reviewed_ids):
        diagnostics.append(
            _diagnostic(
                "ERROR",
                "boundary-review-task-coverage",
                "boundaryReview.taskReviews",
                f"missing review for taskId {task_id!r}.",
            )
        )
    for task_id in sorted(reviewed_ids - task_ids):
        diagnostics.append(
            _diagnostic(
                "ERROR",
                "boundary-review-task-reference",
                f"boundaryReview.taskReviews.{task_id}",
                f"unknown taskId {task_id!r}.",
            )
        )

    for task_id, task_review in task_reviews.items():
        assert isinstance(task_review, dict)
        has_evidence = "indivisibilityEvidence" in task_review
        retained = task_review["preAssignmentDisposition"] == "retained-indivisible"
        accepted = task_review["acceptanceDisposition"] == "accepted-indivisible"
        if has_evidence and not (retained and accepted):
            diagnostics.append(
                _diagnostic(
                    "ERROR",
                    "boundary-review-indivisibility-evidence",
                    f"boundaryReview.taskReviews.{task_id}.indivisibilityEvidence",
                    "is only valid for a retained, accepted-indivisible review.",
                )
            )

    warning_dispositions = review["warningDispositions"]
    assert isinstance(warning_dispositions, dict)
    for warning_id, warning in warning_dispositions.items():
        assert isinstance(warning, dict)
        task_id = warning.get("taskId")
        path = f"boundaryReview.warningDispositions.{warning_id}"
        if task_id is not None and task_id not in task_ids:
            diagnostics.append(
                _diagnostic(
                    "ERROR",
                    "boundary-review-warning-reference",
                    f"{path}.taskId",
                    f"unknown taskId {task_id!r}.",
                )
            )
        if warning["disposition"] == "accepted-indivisible":
            task_review = task_reviews.get(task_id)
            if not isinstance(task_review, dict) or (
                task_review.get("acceptanceDisposition") != "accepted-indivisible"
            ):
                diagnostics.append(
                    _diagnostic(
                        "ERROR",
                        "boundary-review-warning-consistency",
                        path,
                        "accepted-indivisible requires the referenced task review "
                        "to be accepted-indivisible.",
                    )
                )
    return diagnostics


def _validate_metadata(tasks: list[dict[str, Any]]) -> list[str]:
    """Validate required publication metadata and cross-task consistency."""
    diagnostics: list[str] = []
    identities = [task["taskId"] for task in tasks]
    known = set(identities)

    for identity in sorted(known):
        if identities.count(identity) > 1:
            diagnostics.append(
                _diagnostic(
                    "ERROR",
                    "identity",
                    "tasks",
                    f"taskId {identity!r} is duplicated; assign unique task "
                    "identities.",
                )
            )

    for index, task in enumerate(tasks):
        path = f"tasks[{index}]"
        coverage = task["verificationCoverage"]
        if not isinstance(coverage, dict) or not coverage.get("observable"):
            diagnostics.append(
                _diagnostic(
                    "ERROR",
                    "verification-coverage",
                    path,
                    "verificationCoverage.observable must contain at least one "
                    "observable check.",
                )
            )

        dependencies = task["dependencies"]
        if isinstance(dependencies, list):
            for edge_index, edge in enumerate(dependencies):
                if not isinstance(edge, dict):
                    continue  # JSON Schema supplies the precise type diagnostic.
                target = edge.get("taskId")
                edge_path = f"{path}.dependencies[{edge_index}]"
                if target not in known:
                    diagnostics.append(
                        _diagnostic(
                            "ERROR",
                            "dependency-reference",
                            edge_path,
                            f"unknown taskId {target!r}; use one of {sorted(known)!r}.",
                        )
                    )
                elif target == identities[index]:
                    diagnostics.append(
                        _diagnostic(
                            "ERROR",
                            "dependency-cycle",
                            edge_path,
                            "self-reference creates a cycle; reference a prior or "
                            "independent task.",
                        )
                    )

    # Detect cycles only after references have been resolved. Unknown edges are
    # already reported above and are not allowed to masquerade as a cycle.
    graph: dict[str, list[str]] = {identity: [] for identity in identities}
    for index, task in enumerate(tasks):
        dependencies = task.get("dependencies", [])
        for edge in dependencies if isinstance(dependencies, list) else []:
            if isinstance(edge, dict) and edge.get("taskId") in known:
                graph[identities[index]].append(edge["taskId"])

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            diagnostics.append(
                _diagnostic(
                    "ERROR",
                    "dependency-cycle",
                    "tasks",
                    f"dependency graph contains a cycle involving {node!r}; "
                    "remove an edge.",
                )
            )
            return
        if node in visited:
            return
        visiting.add(node)
        for target in graph[node]:
            visit(target)
        visiting.remove(node)
        visited.add(node)

    for identity in identities:
        visit(identity)

    # Overlapping writes are a real publication conflict unless the packet
    # explicitly documents the same tightly coupled publication group.
    owners: dict[str, int] = {}
    for index, task in enumerate(tasks):
        writes = task.get("filesToWrite", [])
        for target in writes if isinstance(writes, list) else []:
            if not isinstance(target, str):
                continue
            previous = owners.get(target)
            if previous is None:
                owners[target] = index
                continue
            left = tasks[previous].get("couplingRationale")
            right = task.get("couplingRationale")
            same_group = (
                isinstance(left, dict)
                and isinstance(right, dict)
                and left.get("group")
                and left.get("group") == right.get("group")
            )
            current_dependencies = task.get("dependencies", [])
            serialized = (
                any(
                    isinstance(edge, dict)
                    and edge.get("taskId") == identities[previous]
                    for edge in current_dependencies
                )
                if isinstance(current_dependencies, list)
                else False
            )
            if not same_group and not serialized:
                diagnostics.append(
                    _diagnostic(
                        "ERROR",
                        "write-target-conflict",
                        f"tasks[{index}].filesToWrite",
                        f"write target {target!r} is also owned by tasks[{previous}]; "
                        "split the target or document one shared coupling group.",
                    )
                )
    return diagnostics


def validate(packet: Any, schema: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a complete canonical task-packet against the packet schema.

    Performs both JSON Schema validation (via *jsonschema*) and custom checks:

    * required keys present per the TaskPacket definition
    * ``purpose`` maxLength 200
    * ``context`` maxLength 8000
    * ``expectedOutput`` maxLength 2000
    * ``executionInstructions`` steps are sequential starting at 1
    * ``filesToRead`` / ``filesToWrite`` entries are unique, non-empty strings
    * (empty arrays are allowed)
    * type correctness via JSON Schema validation

    Args:
        packet: Canonical packet root containing packet metadata, tasks, and closed
            boundary-review evidence. Rootless task arrays are rejected.
        schema: The full task-packet JSON Schema (with definitions).

    Returns:
        ``(True, diagnostics)`` when no structural error exists. A successful result
        is structural-interface evidence only; it is not semantic atomicity approval.
    """
    root_valid, root_errors = validate_root(packet, schema)
    if not root_valid:
        return False, root_errors
    assert isinstance(packet, dict)
    tasks = packet["tasks"]
    assert isinstance(tasks, list)
    errors: list[str] = []

    for idx, task in enumerate(tasks):
        path = f"tasks[{idx}]"
        assert isinstance(task, dict)

        # --- Custom: execution instruction step numbering ---
        steps: Any = task.get("executionInstructions")
        if isinstance(steps, list) and steps:
            errors.extend(_validate_execution_steps(steps, path))

        # --- Custom: file arrays ---
        for arr_field in ("filesToRead", "filesToWrite"):
            arr: Any = task.get(arr_field)
            if isinstance(arr, list):
                errors.extend(_validate_file_array(arr, path, arr_field))

    diagnostics = _validate_metadata(tasks)
    errors.extend(diagnostics)

    hard_errors = [error for error in errors if error.startswith("ERROR ")]
    # Unprefixed structural errors remain hard.
    hard_errors.extend(
        error for error in errors if not error.startswith(("WARNING ", "ERROR "))
    )
    if hard_errors:
        return False, errors
    return True, errors


def auto_fix(tasks: list[dict[str, Any]]) -> bool:
    """Fix skills-only structural errors in task objects.

    Applies fixes deterministically for purely structural skills errors:
    * maxItems exceeded — trim to first 3
    * uniqueItems violated — deduplicate keeping first occurrence
    * empty strings in array — remove

    Does NOT:
    * remove unknown skill names (requires skill inventory)
    * add fallback skills (requires skill inventory)
    * fix non-skills errors

    Args:
        tasks: List of task dicts to fix (modified in place).
    Returns:
        ``True`` when at least one skills array changed.
    """
    changed = False
    for task in tasks:
        skills = task.get("skills")
        if not isinstance(skills, list):
            continue

        normalized = [skill for skill in skills if skill != ""]
        seen: set[str] = set()
        deduped: list[str] = []
        for skill in normalized:
            if skill not in seen:
                seen.add(skill)
                deduped.append(skill)
        normalized = deduped[:3]
        if normalized != skills:
            task["skills"] = normalized
            changed = True
    return changed


def auto_fix_task_structure(
    state_path: str | Path, schema: dict[str, Any]
) -> dict[str, Any]:
    """Validate and auto-fix skills-only structural errors in a state file.

    Reads the state file, validates, applies auto-fix for skills-only errors,
    writes back, and re-validates up to 3 times.

    Args:
        state_path: Path to .tasks state file (JSON object with ``tasks`` array).
        schema: The full task-packet JSON Schema.

    Returns:
        ``{"valid": True, "fixed": True}`` when auto-fix resolved all errors,
        ``{"valid": True, "fixed": False}`` when already valid,
        ``{"valid": False, "errors": [...]}`` when errors remain after fix attempts.
    """
    state_path = Path(state_path)

    # Read initial state
    raw = state_path.read_text(encoding="utf-8")
    parsed: object = json.loads(raw)
    root_errors = _root_schema_errors(parsed, schema)
    if root_errors and not _only_repairable_skills_errors(root_errors):
        return {"valid": False, "errors": _format_root_errors(root_errors)}

    # The only permitted pre-validation exception is a skills-array violation
    # that auto_fix() can remove. Every other canonical-root violation is
    # rejected before task checks and, importantly, before any write.
    if not isinstance(parsed, dict) or not isinstance(parsed.get("tasks"), list):
        return {
            "valid": False,
            "errors": _format_root_errors(root_errors),
        }
    tasks = parsed["tasks"]
    if not all(isinstance(task, dict) for task in tasks):
        return {
            "valid": False,
            "errors": _format_root_errors(root_errors),
        }

    fixed = False
    errors: list[str] = []
    for _ in range(3):
        changed = auto_fix(tasks)
        fixed = fixed or changed
        root_errors = _root_schema_errors(parsed, schema)
        if root_errors:
            return {"valid": False, "errors": _format_root_errors(root_errors)}
        root_valid, root_diagnostics = validate_root(parsed, schema)
        if not root_valid:
            return {"valid": False, "errors": root_diagnostics}
        valid, errors = validate(parsed, schema)
        if valid:
            if fixed:
                state_path.write_text(
                    json.dumps(parsed, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
            result: dict[str, Any] = {"valid": True, "fixed": fixed}
            if errors:
                result["diagnostics"] = errors
            return result
        if not changed:
            return {"valid": False, "errors": errors}

    return {"valid": False, "errors": errors}


def _only_repairable_skills_errors(
    errors: list[jsonschema.ValidationError],
) -> bool:
    """Whether every root-schema error is a skills array limit/duplicate error."""
    return bool(errors) and all(
        list(error.absolute_path)[-1:] == ["skills"]
        and error.validator in {"maxItems", "uniqueItems"}
        for error in errors
    )


def _format_root_errors(errors: list[jsonschema.ValidationError]) -> list[str]:
    """Format schema errors consistently with :func:`validate_root`."""
    formatted: list[str] = []
    for error in errors:
        path = ".".join(str(part) for part in error.absolute_path) or "$"
        message = f"{path}: {error.message}"
        boundary_path = list(error.absolute_path)[:1] == ["boundaryReview"]
        missing_boundary_review = "boundaryReview" in error.message
        if boundary_path or missing_boundary_review:
            message = _diagnostic(
                "ERROR",
                "boundary-review-interface",
                path,
                "malformed or missing required boundaryReview evidence: "
                f"{error.message}",
            )
        formatted.append(message)
    return formatted
