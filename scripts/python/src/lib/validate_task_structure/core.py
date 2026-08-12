"""Task structure validation against the task-packet JSON Schema.

Validates task objects for required keys, length constraints,
step numbering, file array rules, and type correctness.
Consumed by: validate-task-structure.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

KNOWN_COMPOUND_SIGNALS = frozenset(
    {
        "implementation-plus-tests",
        "multiple-helpers",
        "analysis-plus-planning",
        "multiple-comparisons",
    }
)


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


def _task_identity(task: dict[str, Any], index: int) -> str:
    """Return an explicit identity, or the stable migration identity."""
    value = task.get("taskId")
    return value if isinstance(value, str) and value else f"task-{index + 1}"


def _validate_metadata(tasks: list[dict[str, Any]]) -> list[str]:
    """Validate publication metadata while keeping legacy packets migratable."""
    diagnostics: list[str] = []
    identities = [_task_identity(task, index) for index, task in enumerate(tasks)]
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
        if "taskId" not in task:
            diagnostics.append(
                _diagnostic(
                    "WARNING",
                    "identity",
                    path,
                    "taskId is absent; migration identity is "
                    f"{identities[index]!r}. Add taskId before relying on cross-packet "
                    "references.",
                )
            )

        coverage = task.get("verificationCoverage")
        # ``verification`` predates this metadata and is a valid migration
        # source when it contains concrete checks.
        if coverage is None and isinstance(task.get("verification"), list):
            coverage = {"observable": task["verification"]}
        if coverage is None:
            diagnostics.append(
                _diagnostic(
                    "WARNING",
                    "verification-coverage",
                    path,
                    "observable verification coverage is absent; add "
                    "verificationCoverage.observable.",
                )
            )
        elif not isinstance(coverage, dict) or not coverage.get("observable"):
            diagnostics.append(
                _diagnostic(
                    "ERROR",
                    "verification-coverage",
                    path,
                    "verificationCoverage.observable must contain at least one "
                    "observable check.",
                )
            )

        alignment = task.get("purposeOutputAlignment")
        if alignment is None:
            diagnostics.append(
                _diagnostic(
                    "WARNING",
                    "purpose-output-alignment",
                    path,
                    "purpose/output mapping is undocumented; add "
                    "purposeOutputAlignment with evidence.",
                )
            )
        elif isinstance(alignment, dict):
            status = alignment.get("status")
            if status == "not-aligned":
                diagnostics.append(
                    _diagnostic(
                        "ERROR",
                        "purpose-output-alignment",
                        path,
                        "purposeOutputAlignment is not-aligned; revise the boundary "
                        "or expectedOutput.",
                    )
                )
            elif status == "needs-review":
                diagnostics.append(
                    _diagnostic(
                        "WARNING",
                        "purpose-output-alignment",
                        path,
                        "purposeOutputAlignment needs-review; provide evidence that "
                        "one result matches the purpose.",
                    )
                )

        signals = task.get("antiPatternSignals")
        if signals is None:
            diagnostics.append(
                _diagnostic(
                    "WARNING",
                    "anti-pattern-signals",
                    path,
                    "known compound-task signals are undocumented; record reviewed "
                    "signals or explicitly none.",
                )
            )
        elif not isinstance(signals, list):
            diagnostics.append(
                _diagnostic(
                    "ERROR",
                    "anti-pattern-signals",
                    path,
                    "antiPatternSignals must be an array of documented signal names.",
                )
            )
        else:
            named_signals = [
                signal for signal in signals if signal in KNOWN_COMPOUND_SIGNALS
            ]
            if "none" in signals and len(signals) > 1:
                diagnostics.append(
                    _diagnostic(
                        "ERROR",
                        "anti-pattern-signals",
                        path,
                        "antiPatternSignals cannot combine 'none' with named signals.",
                    )
                )
            for signal in named_signals:
                diagnostics.append(
                    _diagnostic(
                        "WARNING",
                        f"anti-pattern-{signal}",
                        path,
                        f"declared {signal!r}; split the independent concerns or "
                        "record evidence for one boundary and one result.",
                    )
                )
        purpose = task.get("purpose", "")
        output = task.get("expectedOutput", "")
        effective_signals = (
            [signal for signal in signals if signal != "none"]
            if isinstance(signals, list)
            else []
        )
        if (
            isinstance(purpose, str)
            and isinstance(output, str)
            and (" and " in purpose.lower() or "," in output)
            and not effective_signals
        ):
            diagnostics.append(
                _diagnostic(
                    "WARNING",
                    "compound-task-signal",
                    path,
                    "purpose/output text contains a possible compound-task signal; "
                    "document the signal and boundary evidence. This heuristic does "
                    "not prove independence.",
                )
            )

        writes = task.get("filesToWrite", [])
        if (
            isinstance(writes, list)
            and len(writes) > 1
            and not task.get("couplingRationale")
        ):
            diagnostics.append(
                _diagnostic(
                    "WARNING",
                    "coupling-rationale",
                    path,
                    "multiple write targets lack couplingRationale; document one "
                    "shared result "
                    "or split the task. File count alone is not a rejection rule.",
                )
            )

        dependencies = task.get("dependencies", [])
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


def validate(
    tasks: list[dict[str, Any]], schema: dict[str, Any]
) -> tuple[bool, list[str]]:
    """Validate a list of task objects against the task-packet schema.

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
        tasks: List of task dicts to validate.
        schema: The full task-packet JSON Schema (with definitions).

    Returns:
        ``(True, diagnostics)`` when no hard error exists. Diagnostics may contain
        migration or review warnings. Returns ``(False, diagnostics)`` when a hard
        error exists.
    """
    errors: list[str] = []
    task_schema: dict[str, Any] = schema.get("definitions", {}).get(
        "TaskPacket", schema
    )

    for idx, task in enumerate(tasks):
        path = f"tasks[{idx}]"

        # --- JSON Schema validation ---
        schema_errors: list[str] = []
        try:
            jsonschema.validate(
                task,
                task_schema,
                cls=jsonschema.Draft7Validator,
                format_checker=jsonschema.Draft7Validator.FORMAT_CHECKER,
            )
        except jsonschema.ValidationError as exc:
            schema_errors.append(f"{path}: {exc.message}")

        if schema_errors:
            errors.extend(schema_errors)
            # Continue with custom checks even if schema validation failed
            # to collect all issues at once

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
    # Legacy structural errors do not carry a stage prefix and remain hard.
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
    if not isinstance(parsed, dict) or not isinstance(parsed.get("tasks"), list):
        raise ValueError("state file must contain a JSON object with a 'tasks' array")
    tasks = parsed["tasks"]
    if not all(isinstance(task, dict) for task in tasks):
        raise ValueError("state file tasks must contain JSON objects")

    fixed = False
    errors: list[str] = []
    for _ in range(3):
        changed = auto_fix(tasks)
        fixed = fixed or changed
        valid, errors = validate(tasks, schema)
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
