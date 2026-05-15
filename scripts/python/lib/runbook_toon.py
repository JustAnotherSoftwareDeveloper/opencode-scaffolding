"""TOON runbook loader with v2 workspace support and legacy v1 JSON compatibility.

This module provides functionality to load and validate runbooks in both:
- v2 format: .runbooks/<id>/main.toon with referenced step files in steps/<step-id>.toon
- v1 format: .runbooks/<id>/runbook.json (legacy JSON format)

Expected v2 step index shape in main.toon:
    steps:
      - id: "01-example"
        file: "steps/01-example.toon"
      - id: "02-another"
        path: "steps/02-another.toon"  # 'path' is tolerated as alias for 'file'

Each step file should contain the full step definition with fields like:
    id: "01-example"
    depends_on: []
    worker:
      family: "coding"
      size: "md"
    objective: "Description of the step"
    # ... other step fields
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from toon_format import DecodeOptions, ToonDecodeError, decode


class RunbookLoadError(Exception):
    """Raised when runbook loading or validation fails."""

    def __init__(self, message: str, path: Path | None = None, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.path = path
        self.details = details or {}


class InvariantViolation(RunbookLoadError):
    """Raised when a safety invariant check fails."""
    pass


class ToonValidationError(RunbookLoadError):
    """Raised when TOON parsing fails."""
    pass


@dataclass
class LoadedStep:
    """A loaded step with its source file and parsed data."""
    id: str
    source_file: Path
    data: dict[str, Any]


@dataclass
class RunbookLoadResult:
    """Result of loading a runbook."""
    runbook_id: str
    format_version: int  # 1 for JSON, 2 for TOON
    source_path: Path
    data: dict[str, Any]  # Normalized runbook data
    steps: list[LoadedStep] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class PathValidator(Protocol):
    """Protocol for path validation strategies."""
    def validate(self, runbook_dir: Path, ref_path: str, context: str) -> Path: ...


class StrictStepPathValidator:
    """Validates step reference paths with strict safety rules.
    
    Rules:
    - Must be relative (no leading /)
    - Must start with 'steps/'
    - Must end with '.toon'
    - No '..' components
    - Must resolve within runbook directory
    """
    
    def validate(self, runbook_dir: Path, ref_path: str, context: str) -> Path:
        """Validate and resolve a step reference path.
        
        Args:
            runbook_dir: The runbook directory (.runbooks/<id>)
            ref_path: The reference path from main.toon (e.g., "steps/01-example.toon")
            context: Description for error messages
            
        Returns:
            Resolved absolute path to the step file
            
        Raises:
            InvariantViolation: If path violates safety rules
        """
        # Check for empty path
        if not ref_path:
            raise InvariantViolation(
                f"Empty step reference path in {context}",
                path=runbook_dir
            )
        
        # Check for absolute path
        if ref_path.startswith("/"):
            raise InvariantViolation(
                f"Absolute step path not allowed in {context}: {ref_path}",
                path=runbook_dir,
                details={"ref_path": ref_path, "rule": "no_absolute_paths"}
            )
        
        # Check for parent directory traversal
        if ".." in ref_path.split("/"):
            raise InvariantViolation(
                f"Parent directory traversal not allowed in {context}: {ref_path}",
                path=runbook_dir,
                details={"ref_path": ref_path, "rule": "no_traversal"}
            )
        
        # Check path starts with steps/
        if not ref_path.startswith("steps/"):
            raise InvariantViolation(
                f"Step reference must be under 'steps/' in {context}: {ref_path}",
                path=runbook_dir,
                details={"ref_path": ref_path, "rule": "must_be_in_steps"}
            )
        
        # Check path ends with .toon
        if not ref_path.endswith(".toon"):
            raise InvariantViolation(
                f"Step file must end with '.toon' in {context}: {ref_path}",
                path=runbook_dir,
                details={"ref_path": ref_path, "rule": "must_be_toon"}
            )
        
        # Resolve and verify it's within runbook directory
        step_path = (runbook_dir / ref_path).resolve()
        runbook_resolved = runbook_dir.resolve()
        
        try:
            step_path.relative_to(runbook_resolved)
        except ValueError:
            raise InvariantViolation(
                f"Step path escapes runbook directory in {context}: {ref_path}",
                path=runbook_dir,
                details={"ref_path": ref_path, "resolved": str(step_path), "rule": "path_escape"}
            )
        
        return step_path


def detect_runbook_format(runbook_path: Path) -> int:
    """Detect whether a runbook is v1 JSON or v2 TOON format.
    
    Args:
        runbook_path: Path to the runbook file
        
    Returns:
        1 for JSON format (runbook.json), 2 for TOON format (main.toon)
        
    Raises:
        RunbookLoadError: If format cannot be determined
    """
    if runbook_path.name == "runbook.json":
        return 1
    elif runbook_path.name == "main.toon":
        return 2
    else:
        raise RunbookLoadError(
            f"Cannot detect runbook format from filename: {runbook_path.name}. "
            "Expected 'runbook.json' (v1) or 'main.toon' (v2).",
            path=runbook_path
        )


def load_json_runbook(runbook_path: Path) -> dict[str, Any]:
    """Load a v1 JSON runbook.
    
    Args:
        runbook_path: Path to runbook.json
        
    Returns:
        Parsed runbook data
        
    Raises:
        RunbookLoadError: If loading fails
    """
    try:
        with open(runbook_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise RunbookLoadError(f"Runbook file not found: {runbook_path}", path=runbook_path)
    except json.JSONDecodeError as e:
        raise RunbookLoadError(
            f"Invalid JSON in runbook: {e}",
            path=runbook_path,
            details={"line": e.lineno, "column": e.colno}
        )


def load_toon_strict(source: str | Path) -> dict[str, Any]:
    """Load TOON content in strict mode, requiring object root.
    
    Args:
        source: TOON string or file path
        
    Returns:
        Parsed TOON data as dict (must be an object)
        
    Raises:
        ToonValidationError: If parsing fails or root is not an object
    """
    try:
        if isinstance(source, Path):
            with open(source, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = source
        result = decode(content, DecodeOptions(strict=True))
        if not isinstance(result, dict):
            raise ToonValidationError(
                f"TOON root must be an object, got {type(result).__name__}: {result}",
                path=source if isinstance(source, Path) else None
            )
        return result
    except ToonDecodeError as e:
        raise ToonValidationError(
            f"TOON parsing failed: {e}",
            path=source if isinstance(source, Path) else None
        )
    except FileNotFoundError:
        raise ToonValidationError(f"TOON file not found: {source}", path=source if isinstance(source, Path) else None)


def validate_path_shape(runbook_path: Path) -> tuple[str, Path]:
    """Validate the runbook path shape and extract the runbook ID.
    
    Expected shapes:
    - v2: .runbooks/<id>/main.toon
    - v1: .runbooks/<id>/runbook.json
    
    Args:
        runbook_path: Path to the runbook file
        
    Returns:
        Tuple of (runbook_id, runbook_dir)
        
    Raises:
        InvariantViolation: If path shape is invalid
    """
    resolved = runbook_path.resolve()
    
    # Check parent.parent is .runbooks
    if resolved.parent.parent.name != ".runbooks":
        raise InvariantViolation(
            f"Runbook must be in .runbooks/<id>/ directory, got: {resolved}",
            path=runbook_path,
            details={"expected": ".runbooks/<id>/main.toon or .runbooks/<id>/runbook.json"}
        )
    
    runbook_id = resolved.parent.name
    runbook_dir = resolved.parent
    
    return runbook_id, runbook_dir


def validate_runbook_id_matches(runbook_data: dict[str, Any], expected_id: str, runbook_path: Path) -> None:
    """Validate that runbook id matches directory name.
    
    Args:
        runbook_data: Parsed runbook data
        expected_id: Expected runbook ID (from directory name)
        runbook_path: Path to runbook for error reporting
        
    Raises:
        InvariantViolation: If ID doesn't match
    """
    actual_id = runbook_data.get("id")
    if not actual_id:
        raise InvariantViolation(
            "Runbook missing required 'id' field",
            path=runbook_path
        )
    
    if actual_id != expected_id:
        raise InvariantViolation(
            f"Runbook id mismatch: directory is '{expected_id}' but runbook has '{actual_id}'",
            path=runbook_path,
            details={"expected_id": expected_id, "actual_id": actual_id}
        )


def validate_state_dir(runbook_data: dict[str, Any], runbook_id: str, runbook_path: Path) -> None:
    """Validate the state_dir field.
    
    Args:
        runbook_data: Parsed runbook data
        runbook_id: Expected runbook ID
        runbook_path: Path to runbook for error reporting
        
    Raises:
        InvariantViolation: If state_dir is invalid
    """
    state_dir = runbook_data.get("state_dir")
    if not state_dir:
        raise InvariantViolation(
            "Runbook missing required 'state_dir' field",
            path=runbook_path
        )
    
    expected = f"../../.state/{runbook_id}/"
    if state_dir != expected:
        raise InvariantViolation(
            f"Invalid state_dir: expected '{expected}', got '{state_dir}'",
            path=runbook_path,
            details={"expected": expected, "actual": state_dir}
        )


def load_step_files(
    runbook_dir: Path,
    steps_index: list[dict[str, Any]],
    path_validator: PathValidator | None = None
) -> list[LoadedStep]:
    """Load referenced step files from the steps/ directory.
    
    Args:
        runbook_dir: The runbook directory (.runbooks/<id>)
        steps_index: Array of step index entries from main.toon
        path_validator: Validator for step reference paths
        
    Returns:
        List of loaded steps
        
    Raises:
        InvariantViolation: If step loading fails validation
    """
    if path_validator is None:
        path_validator = StrictStepPathValidator()
    
    loaded_steps: list[LoadedStep] = []
    seen_ids: set[str] = set()
    
    for idx, step_ref in enumerate(steps_index):
        step_id = step_ref.get("id")
        if not step_id:
            raise InvariantViolation(
                f"Step index entry {idx} missing required 'id' field",
                path=runbook_dir,
                details={"index": idx, "entry": step_ref}
            )
        
        # Check for duplicate IDs
        if step_id in seen_ids:
            raise InvariantViolation(
                f"Duplicate step id in index: '{step_id}'",
                path=runbook_dir,
                details={"step_id": step_id, "index": idx}
            )
        seen_ids.add(step_id)
        
        # Get file reference (support 'file' primary, 'path' as alias)
        file_ref = step_ref.get("file") or step_ref.get("path")
        if not file_ref:
            raise InvariantViolation(
                f"Step '{step_id}' missing file reference (expected 'file' or 'path' field)",
                path=runbook_dir,
                details={"step_id": step_id, "index": idx}
            )
        
        # Validate and resolve path
        step_path = path_validator.validate(
            runbook_dir,
            file_ref,
            f"step '{step_id}' at index {idx}"
        )
        
        # Check file exists
        if not step_path.exists():
            raise InvariantViolation(
                f"Step file not found for '{step_id}': {file_ref}",
                path=runbook_dir,
                details={"step_id": step_id, "ref_path": file_ref}
            )
        
        # Load and parse step file
        try:
            step_data = load_toon_strict(step_path)
        except ToonValidationError as e:
            raise InvariantViolation(
                f"Failed to load step '{step_id}': {e}",
                path=step_path,
                details={"step_id": step_id, "original_error": str(e)}
            )
        
        # Validate step file id matches
        file_step_id = step_data.get("id")
        if file_step_id != step_id:
            raise InvariantViolation(
                f"Step ID mismatch: index has '{step_id}' but file has '{file_step_id}'",
                path=step_path,
                details={"index_id": step_id, "file_id": file_step_id}
            )
        
        # Validate filename stem matches step id
        if step_path.stem != step_id:
            raise InvariantViolation(
                f"Step filename mismatch: step id '{step_id}' should have filename '{step_id}.toon'",
                path=step_path,
                details={"step_id": step_id, "filename": step_path.name}
            )
        
        loaded_steps.append(LoadedStep(
            id=step_id,
            source_file=step_path,
            data=step_data
        ))
    
    return loaded_steps


def check_unreferenced_step_files(
    runbook_dir: Path,
    loaded_steps: list[LoadedStep],
    allow_unreferenced: bool = False
) -> list[str]:
    """Check for unreferenced .toon files in the steps/ directory.
    
    Args:
        runbook_dir: The runbook directory
        loaded_steps: List of steps that were referenced
        allow_unreferenced: If True, return warnings instead of raising
        
    Returns:
        List of warning messages (empty if no issues)
        
    Raises:
        InvariantViolation: If unreferenced files exist and allow_unreferenced is False
    """
    steps_dir = runbook_dir / "steps"
    if not steps_dir.exists():
        return []
    
    referenced_files = {step.source_file.resolve() for step in loaded_steps}
    warnings: list[str] = []
    
    for toon_file in steps_dir.glob("*.toon"):
        if toon_file.resolve() not in referenced_files:
            msg = f"Unreferenced step file: {toon_file.relative_to(runbook_dir)}"
            if allow_unreferenced:
                warnings.append(msg)
            else:
                raise InvariantViolation(
                    f"{msg}. Either reference it in main.toon or remove it.",
                    path=toon_file,
                    details={"file": str(toon_file)}
                )
    
    return warnings


def validate_dependency_graph(
    runbook_data: dict[str, Any],
    valid_step_ids: set[str],
    runbook_path: Path
) -> None:
    """Validate the dependency_graph field and step-level depends_on fields.
    
    Args:
        runbook_data: Runbook data containing dependency_graph and steps
        valid_step_ids: Set of valid step IDs
        runbook_path: Path for error reporting
        
    Raises:
        InvariantViolation: If dependency graph is invalid
    """
    # Build combined dependency map from both dependency_graph and step-level depends_on
    combined_deps: dict[str, list[str]] = {}
    
    # Initialize with dependency_graph
    dep_graph = runbook_data.get("dependency_graph", {})
    for step_id, deps in dep_graph.items():
        if step_id not in combined_deps:
            combined_deps[step_id] = []
        combined_deps[step_id].extend(deps)
    
    # Add step-level depends_on references
    steps = runbook_data.get("steps", [])
    for step in steps:
        step_id = step.get("id")
        if not step_id:
            continue
        deps = step.get("depends_on", [])
        if step_id not in combined_deps:
            combined_deps[step_id] = []
        combined_deps[step_id].extend(deps)
    
    # Check all referenced steps exist
    for step_id, deps in combined_deps.items():
        if step_id not in valid_step_ids:
            raise InvariantViolation(
                f"Dependency references unknown step: '{step_id}'",
                path=runbook_path,
                details={"step_id": step_id, "valid_steps": sorted(valid_step_ids)}
            )
        
        for dep in deps:
            if dep not in valid_step_ids:
                raise InvariantViolation(
                    f"Step '{step_id}' depends_on unknown step: '{dep}'",
                    path=runbook_path,
                    details={"step_id": step_id, "dependency": dep, "valid_steps": sorted(valid_step_ids)}
                )
    
    # Check for cycles using DFS on combined dependencies
    def has_cycle(start: str, visited: set[str], rec_stack: set[str]) -> list[str] | None:
        """Return cycle path if cycle found, None otherwise."""
        visited.add(start)
        rec_stack.add(start)
        
        for neighbor in combined_deps.get(start, []):
            if neighbor not in visited:
                cycle = has_cycle(neighbor, visited, rec_stack)
                if cycle:
                    return [start] + cycle
            elif neighbor in rec_stack:
                return [start, neighbor]
        
        rec_stack.remove(start)
        return None
    
    visited: set[str] = set()
    for step_id in combined_deps:
        if step_id not in visited:
            cycle = has_cycle(step_id, visited, set())
            if cycle:
                raise InvariantViolation(
                    f"Circular dependency detected: {' -> '.join(cycle)}",
                    path=runbook_path,
                    details={"cycle": cycle}
                )


def validate_parallel_groups(
    runbook_data: dict[str, Any],
    valid_step_ids: set[str],
    runbook_path: Path
) -> None:
    """Validate parallel_groups field.
    
    Args:
        runbook_data: Runbook data containing parallel_groups
        valid_step_ids: Set of valid step IDs
        runbook_path: Path for error reporting
        
    Raises:
        InvariantViolation: If parallel groups are invalid
    """
    parallel_groups = runbook_data.get("parallel_groups", {})
    if not parallel_groups:
        return
    
    for group_name, group_steps in parallel_groups.items():
        for step_id in group_steps:
            if step_id not in valid_step_ids:
                raise InvariantViolation(
                    f"Parallel group '{group_name}' references unknown step: '{step_id}'",
                    path=runbook_path,
                    details={"group": group_name, "step_id": step_id}
                )


def validate_required_fields(
    runbook_data: dict[str, Any],
    runbook_path: Path,
    format_version: int
) -> None:
    """Validate that required fields are present according to v1/v2 contract.
    
    Args:
        runbook_data: Runbook data
        runbook_path: Path for error reporting
        format_version: 1 for JSON, 2 for TOON
        
    Raises:
        InvariantViolation: If required fields are missing
    """
    # Required runbook-level fields (v1 and v2)
    required_runbook_fields = [
        "id", "title", "objective", "plan_summary", "inputs", "constraints", 
        "execution_strategy", "delegation_map", "steps", "dependency_graph", 
        "parallel_groups", "state_initialization", "verification_gates", 
        "embedded_quality_check", "rollback_recovery", "final_report_contract", "status", "created_at", "updated_at", "proposal", "plan", "active_step"
    ]
    
    for field in required_runbook_fields:
        if field not in runbook_data:
            raise InvariantViolation(
                f"Runbook missing required field: '{field}'",
                path=runbook_path
            )
    
    # Format-specific requirements
    if format_version == 2:
        # v2 requires format_version
        if not runbook_data.get("format_version"):
            raise InvariantViolation(
                "v2 runbook must specify 'format_version' field",
                path=runbook_path
            )
    else:
        # v1 requires schema_version
        if not runbook_data.get("schema_version"):
            raise InvariantViolation(
                "v1 runbook must specify 'schema_version' field",
                path=runbook_path
            )
    
    # Validate steps have required fields
    steps = runbook_data.get("steps", [])
    for idx, step in enumerate(steps):
        step_id = step.get("id", f"<index {idx}>")
        
        # Required step fields
        required_step_fields = [
            "id", "depends_on", "parallel_group", "worker", "skill", 
            "minimum_capable_tier", "context_package", "objective", 
            "expected_output", "state_updates", "acceptance_criteria", 
            "verification", "recovery"
        ]
        
        for field in required_step_fields:
            if field not in step:
                raise InvariantViolation(
                    f"Step '{step_id}' missing required field: '{field}'",
                    path=runbook_path
                )
        
        # Validate worker field structure
        worker = step.get("worker")
        if worker is None:
            raise InvariantViolation(
                f"Step '{step_id}' missing required 'worker' field",
                path=runbook_path
            )
        
        if "family" not in worker:
            raise InvariantViolation(
                f"Step '{step_id}' worker missing required 'family' field",
                path=runbook_path
            )
        
        if "size" not in worker:
            raise InvariantViolation(
                f"Step '{step_id}' worker missing required 'size' field",
                path=runbook_path
            )
        
        # Validate context_package structure
        context_package = step.get("context_package")
        if context_package is None:
            raise InvariantViolation(
                f"Step '{step_id}' missing required 'context_package' field",
                path=runbook_path
            )
        
        required_context_fields = [
            "user_requirement_slice", "relevant_proposal_sections", 
            "relevant_state_files", "files_in_scope", "files_out_scope", 
            "expected_return_format"
        ]
        
        for field in required_context_fields:
            if field not in context_package:
                raise InvariantViolation(
                    f"Step '{step_id}' context_package missing required field: '{field}'",
                    path=runbook_path
                )
        
        # Validate context package fields that must be non-empty when present
        if not context_package.get("user_requirement_slice"):
            raise InvariantViolation(
                f"Step '{step_id}' context_package.user_requirement_slice must be a non-empty string",
                path=runbook_path
            )
        
        if not context_package.get("expected_return_format"):
            raise InvariantViolation(
                f"Step '{step_id}' context_package.expected_return_format must be a non-empty string",
                path=runbook_path
            )
        
        # Validate context package arrays are present (can be empty)
        for array_field in ["relevant_proposal_sections", "relevant_state_files", "files_in_scope", "files_out_scope"]:
            if array_field not in context_package:
                raise InvariantViolation(
                    f"Step '{step_id}' context_package missing required array field: '{array_field}'",
                    path=runbook_path
                )
            if not isinstance(context_package[array_field], list):
                raise InvariantViolation(
                    f"Step '{step_id}' context_package.{array_field} must be an array",
                    path=runbook_path
                )


def validate_active_step(
    runbook_data: dict[str, Any],
    valid_step_ids: set[str],
    runbook_path: Path
) -> None:
    """Validate active_step field if present.
    
    Args:
        runbook_data: Runbook data
        valid_step_ids: Set of valid step IDs
        runbook_path: Path for error reporting
        
    Raises:
        InvariantViolation: If active_step is invalid
    """
    # active_step may be null or missing, but if present, it must be valid
    active_step = runbook_data.get("active_step")
    if active_step is not None and active_step not in valid_step_ids:
        raise InvariantViolation(
            f"active_step references unknown step: '{active_step}'",
            path=runbook_path,
            details={"active_step": active_step, "valid_steps": sorted(valid_step_ids)}
        )


def merge_step_data(
    main_data: dict[str, Any],
    loaded_steps: list[LoadedStep]
) -> list[dict[str, Any]]:
    """Merge loaded step data into normalized step list.
    
    Preserves order from main.toon steps index, merging full step data
    from individual step files.
    
    Args:
        main_data: The main.toon data with steps index
        loaded_steps: List of loaded step files
        
    Returns:
        Normalized list of step data compatible with seed_runbook_state
    """
    steps_by_id = {step.id: step.data for step in loaded_steps}
    steps_index = main_data.get("steps", [])
    
    merged: list[dict[str, Any]] = []
    for step_ref in steps_index:
        step_id = step_ref.get("id")
        if step_id and step_id in steps_by_id:
            merged.append(steps_by_id[step_id])
    
    return merged


def load_runbook(
    runbook_path: str | Path,
    allow_unreferenced_steps: bool = False
) -> RunbookLoadResult:
    """Load and validate a runbook in either v1 JSON or v2 TOON format.
    
    This is the main entry point for runbook loading. It handles both:
    - v1: .runbooks/<id>/runbook.json (legacy JSON)
    - v2: .runbooks/<id>/main.toon with steps/*.toon files
    
    Args:
        runbook_path: Path to runbook.json (v1) or main.toon (v2)
        allow_unreferenced_steps: If True, warn instead of error on unreferenced step files
        
    Returns:
        RunbookLoadResult containing normalized data
        
    Raises:
        RunbookLoadError: If loading or validation fails
        InvariantViolation: If safety invariants are violated
        
    Example:
        >>> result = load_runbook(".runbooks/my-runbook/main.toon")
        >>> print(f"Loaded {len(result.steps)} steps")
        >>> # Access normalized data
        >>> runbook_data = result.data
    """
    runbook_path = Path(runbook_path).resolve()
    
    # Detect format
    format_version = detect_runbook_format(runbook_path)
    
    # Validate path shape and get runbook info
    runbook_id, runbook_dir = validate_path_shape(runbook_path)
    
    warnings: list[str] = []
    
    if format_version == 1:
        # Load legacy JSON format
        runbook_data = load_json_runbook(runbook_path)
        loaded_steps = []
        
    else:
        # Load v2 TOON format
        main_data = load_toon_strict(runbook_path)
        
        # Validate runbook ID matches directory
        validate_runbook_id_matches(main_data, runbook_id, runbook_path)
        
        # Validate state_dir
        validate_state_dir(main_data, runbook_id, runbook_path)
        
        # Load referenced step files
        steps_index = main_data.get("steps", [])
        if not isinstance(steps_index, list):
            raise InvariantViolation(
                "main.toon 'steps' field must be an array of step index objects",
                path=runbook_path,
                details={"type": type(steps_index).__name__}
            )
        
        loaded_steps = load_step_files(runbook_dir, steps_index)
        
        # Check for unreferenced step files
        warnings = check_unreferenced_step_files(
            runbook_dir, loaded_steps, allow_unreferenced_steps
        )
        
        # Merge step data into normalized format
        merged_steps = merge_step_data(main_data, loaded_steps)
        
        # Build normalized runbook data (JSON-compatible)
        runbook_data = dict(main_data)
        runbook_data["steps"] = merged_steps
    
    # Common validations for both formats
    validate_runbook_id_matches(runbook_data, runbook_id, runbook_path)
    validate_state_dir(runbook_data, runbook_id, runbook_path)
    validate_required_fields(runbook_data, runbook_path, format_version)
    
    # Get valid step IDs for graph validation
    valid_step_ids = {step.id for step in loaded_steps} if format_version == 2 else {
        step.get("id") for step in runbook_data.get("steps", []) if step.get("id")
    }
    
    # Validate dependency graph
    validate_dependency_graph(runbook_data, valid_step_ids, runbook_path)
    
    # Validate parallel groups
    validate_parallel_groups(runbook_data, valid_step_ids, runbook_path)
    
    # Validate active_step
    validate_active_step(runbook_data, valid_step_ids, runbook_path)
    
    return RunbookLoadResult(
        runbook_id=runbook_id,
        format_version=format_version,
        source_path=runbook_path,
        data=runbook_data,
        steps=loaded_steps,
        warnings=warnings
    )


def validate_runbook(
    runbook_path: str | Path,
    strict: bool = True
) -> tuple[bool, list[str]]:
    """Validate a runbook file without loading full data.
    
    Args:
        runbook_path: Path to runbook file
        strict: If True, treat warnings as errors
        
    Returns:
        Tuple of (is_valid, list of messages)
    """
    messages: list[str] = []
    
    try:
        result = load_runbook(runbook_path, allow_unreferenced_steps=not strict)
        messages.append(f"✓ Runbook loaded successfully: {result.runbook_id}")
        messages.append(f"✓ Format: v{result.format_version}")
        messages.append(f"✓ Steps: {len(result.steps) if result.steps else len(result.data.get('steps', []))}")
        
        if result.warnings:
            if strict:
                messages.append("✗ Warnings (treated as errors in strict mode):")
                for w in result.warnings:
                    messages.append(f"  - {w}")
                return False, messages
            else:
                messages.append("⚠ Warnings:")
                for w in result.warnings:
                    messages.append(f"  - {w}")
        
        return True, messages
        
    except RunbookLoadError as e:
        messages.append(f"✗ Validation failed: {e}")
        if e.details:
            for key, value in e.details.items():
                messages.append(f"  {key}: {value}")
        return False, messages
    except Exception as e:
        messages.append(f"✗ Unexpected error: {e}")
        return False, messages


# Export key items for convenience
__all__ = [
    "load_runbook",
    "validate_runbook",
    "RunbookLoadResult",
    "LoadedStep",
    "RunbookLoadError",
    "InvariantViolation",
    "ToonValidationError",
    "detect_runbook_format",
    "load_toon_strict",
    "StrictStepPathValidator",
]
