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
        ``(True, [])`` if all tasks are valid,
        ``(False, [error_messages])`` with descriptive messages otherwise.
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

    if errors:
        return False, errors
    return True, []


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
            return {"valid": True, "fixed": fixed}
        if not changed:
            return {"valid": False, "errors": errors}

    return {"valid": False, "errors": errors}
