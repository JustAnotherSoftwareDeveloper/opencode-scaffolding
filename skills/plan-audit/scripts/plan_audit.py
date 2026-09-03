#!/usr/bin/env python3
"""Read-only, report-only plan audit implementation.

The module intentionally keeps the audit implementation inside the operation
workspace.  It exposes ``audit`` for focused tests and a small CLI for callers.
The only successful filesystem mutation is creation of the caller's new report.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.parse import unquote

try:
    import yaml
except ImportError:  # pragma: no cover - the repository project supplies PyYAML
    yaml = None  # type: ignore[assignment]


DISPOSITIONS = {"PASS", "CONDITIONAL PASS", "FAIL", "BLOCKED"}
DIAGNOSTIC_STATUSES = {"WARNING", "NOT OBSERVABLE", "BLOCKED", "FAIL"}
PROPOSAL_REQUIRED_SECTIONS = [
    "table of contents",
    "recommendation",
    "technical rationale",
    "questions",
    "options considered",
    "implementation details",
    "verification criteria",
    "sources",
]
CANONICAL_PROPOSAL_FILES: list[str] = ["PROPOSAL.md"]
COLLECTOR_COMMAND = (
    "uv run --project ~/.config/opencode/scripts/python collect-skills "
    "--class operation --class documentation"
)
COLLECTOR_ARGS = [
    "uv",
    "run",
    "--project",
    str(Path.home() / ".config" / "opencode" / "scripts" / "python"),
    "collect-skills",
    "--class",
    "operation",
    "--class",
    "documentation",
]
LINK_RE = re.compile(r"\]\(([^)]+)\)")
PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_PROJECT = PROJECT_ROOT / "scripts" / "python"
TASK_SCHEMA = PROJECT_ROOT / "skills" / "breakdown-tasks" / "schema" / "task-packet.schema.json"
STOPWORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "into", "of",
    "on", "or", "the", "to", "under", "use", "when", "with",
}
TOC_HEADING_RE = re.compile(r"^(#{2,3}) (.+?)(?:\s+#+)?$")


class AuditInputError(ValueError):
    """A normalized input cannot satisfy the report boundary."""


@dataclass(frozen=True)
class NormalizedInput:
    plan_workspace: Path
    proposal_mode: str
    proposal_root: Path
    audit_output: Path
    workspace_root: Path
    persisted_inventory: Path | None = None
    copied_origin_identity: str | None = None
    copied_capture_time: str | None = None
    copied_manifest: Any = None
    unavailable_reason: str | None = None
    comparison_snapshot: Path | None = None
    comparison_origin_identity: str | None = None
    comparison_capture_time: str | None = None
    comparison_manifest: Any = None


@dataclass
class Diagnostic:
    id: str
    status: str
    criterion: str
    location: str
    observed: str
    expected: str
    impact: str
    confidence: str
    message: str


@dataclass
class CheckResult:
    name: str
    disposition: str
    coverage: str
    confidence: str
    criteria: list[str] = field(default_factory=list)
    diagnostics: list[Diagnostic] = field(default_factory=list)
    evidence_gaps: list[str] = field(default_factory=list)


@dataclass
class CollectorResult:
    ok: bool
    records: list[dict[str, Any]]
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0
    cwd: str = ""
    captured_at: str = ""
    output_digest: str = ""


@dataclass
class AuditResult:
    audit_id: str
    overall: str
    report_path: Path
    report: str
    checks: list[CheckResult]
    manifest: list[dict[str, Any]]
    collector: CollectorResult
    wrote_report: bool


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _text_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _resolve(value: str | os.PathLike[str], base: Path) -> Path:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = base / candidate
    return candidate.resolve(strict=False)


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def normalize_input(raw: Mapping[str, Any], *, workspace_root: Path | None = None) -> NormalizedInput:
    """Normalize the exact public input object without reading audited files."""
    required = {"planWorkspace", "proposalBaseline", "assignmentInventory", "auditOutput"}
    missing = required.difference(raw)
    if missing:
        raise AuditInputError(f"missing normalized input fields: {', '.join(sorted(missing))}")
    root = (workspace_root or Path.cwd()).resolve()
    plan = _resolve(str(raw["planWorkspace"]), root)
    baseline = raw["proposalBaseline"]
    if not isinstance(baseline, Mapping):
        raise AuditInputError("proposalBaseline must be an object")
    mode = str(baseline.get("mode", "authoritative"))
    if mode not in {"authoritative", "copied-snapshot"}:
        raise AuditInputError("proposalBaseline.mode must be authoritative or copied-snapshot")
    if not baseline.get("root"):
        raise AuditInputError("proposalBaseline.root is required")
    proposal = _resolve(str(baseline["root"]), root)
    output = _resolve(str(raw["auditOutput"]), root)
    persisted_value = raw.get("assignmentInventory")
    persisted: Path | None = None
    if persisted_value:
        if isinstance(persisted_value, Mapping):
            persisted_value = persisted_value.get("path")
        if persisted_value:
            persisted = _resolve(str(persisted_value), root)
    comparison = baseline.get("comparisonSnapshot")
    comparison_root: Path | None = None
    if comparison:
        if not isinstance(comparison, Mapping) or not comparison.get("root"):
            raise AuditInputError("comparisonSnapshot.root is required")
        comparison_root = _resolve(str(comparison["root"]), root)
    if not _inside(output, root):
        raise AuditInputError("auditOutput must be under the workspace root")
    if output.exists():
        raise AuditInputError("auditOutput already exists; refusing overwrite")
    if not output.parent.is_dir():
        raise AuditInputError("auditOutput parent must already exist")
    if not plan.is_dir():
        raise AuditInputError("planWorkspace must be an existing directory")
    audited_roots = [plan, proposal]
    if comparison_root:
        audited_roots.append(comparison_root)
    if persisted:
        audited_roots.append(persisted)
    if any(_inside(output, item) for item in audited_roots):
        raise AuditInputError("auditOutput must be outside every declared audited tree")
    if mode == "copied-snapshot":
        reason = str(baseline.get("unavailableReason", "")).strip()
        origin = str(baseline.get("originIdentity", "")).strip()
        capture = str(baseline.get("captureTime", "")).strip()
        if not reason or not origin or not capture:
            raise AuditInputError(
                "copied-snapshot requires unavailableReason, originIdentity, and captureTime"
            )
        if not baseline.get("manifest"):
            raise AuditInputError("copied-snapshot requires a per-file manifest")
    return NormalizedInput(
        plan_workspace=plan,
        proposal_mode=mode,
        proposal_root=proposal,
        audit_output=output,
        workspace_root=root,
        persisted_inventory=persisted,
        copied_origin_identity=str(baseline.get("originIdentity")) if baseline.get("originIdentity") else None,
        copied_capture_time=str(baseline.get("captureTime")) if baseline.get("captureTime") else None,
        copied_manifest=baseline.get("manifest"),
        unavailable_reason=str(baseline.get("unavailableReason")) if baseline.get("unavailableReason") else None,
        comparison_snapshot=comparison_root,
        comparison_origin_identity=(
            str(comparison.get("originIdentity")) if isinstance(comparison, Mapping) and comparison.get("originIdentity") else None
        ),
        comparison_capture_time=(
            str(comparison.get("captureTime")) if isinstance(comparison, Mapping) and comparison.get("captureTime") else None
        ),
        comparison_manifest=(comparison.get("manifest") if isinstance(comparison, Mapping) else None),
    )


def _read_utf8(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _tree_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    if root.is_file():
        return [root]
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise AuditInputError(f"symlink is not an immutable regular input: {path}")
        if path.is_file():
            files.append(path)
    return files


def _manifest_tree(root: Path, label: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for path in _tree_files(root):
        try:
            data = path.read_bytes()
        except OSError as exc:
            raise AuditInputError(f"cannot read audited input {path}: {exc}") from exc
        relative = path.relative_to(root).as_posix() if root.is_dir() else path.name
        result.append(
            {
                "tree": label,
                "path": relative,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "resolved": str(path),
            }
        )
    return result


def _manifest_file(path: Path, label: str) -> list[dict[str, Any]]:
    return _manifest_tree(path, label) if path.is_dir() else _manifest_tree(path, label)


def _manifest_by_key(entries: Iterable[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {(entry["tree"], entry["path"]): entry for entry in entries}


def _finding_id(family: str, criterion: str, location: str, expected: str, observed: str) -> str:
    material = "|".join((family, criterion, location, _text_digest(expected), _text_digest(observed)))
    return f"{family}-{criterion}-{hashlib.sha256(material.encode('utf-8')).hexdigest()[:12]}"


def _diag(
    family: str,
    status: str,
    criterion: str,
    location: str,
    observed: str,
    expected: str,
    impact: str,
    message: str,
    confidence: str = "HIGH",
) -> Diagnostic:
    return Diagnostic(
        id=_finding_id(family, criterion, location, expected, observed),
        status=status,
        criterion=criterion,
        location=location,
        observed=observed,
        expected=expected,
        impact=impact,
        confidence=confidence,
        message=message,
    )


def _disposition(diagnostics: list[Diagnostic], blocked: bool = False) -> str:
    if blocked or any(item.status == "BLOCKED" for item in diagnostics):
        return "BLOCKED"
    if any(item.status == "FAIL" for item in diagnostics):
        return "FAIL"
    if any(item.status in {"WARNING", "NOT OBSERVABLE"} for item in diagnostics):
        return "CONDITIONAL PASS"
    return "PASS"


def _frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}
    if yaml is None:
        return {}
    try:
        value = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError:
        return {}
    return value if isinstance(value, dict) else {}


def _links(text: str) -> list[str]:
    values: list[str] = []
    for raw in LINK_RE.findall(text):
        target = raw.split("#", 1)[0].strip()
        if target and not re.match(r"^[a-z]+://", target):
            values.append(unquote(target))
    return values


def _unresolved_label_statements(text: str) -> list[str]:
    pattern = re.compile(
        r"(?im)^\s*(?:[-*]\s+)?(?:\*\*)?(Assumption:|Evidence Gap:|Open Question:)"
        r"(?:\*\*)?\s*(.+?)\s*$"
    )
    return [f"{label} {statement}".strip() for label, statement in pattern.findall(text)]


def _markdown_anchor(heading: str) -> str:
    anchor = heading.lower()
    anchor = re.sub(r"[^\w\s-]", "", anchor)
    anchor = re.sub(r"\s+", "-", anchor)
    anchor = re.sub(r"-+", "-", anchor)
    return anchor.strip("-")


def _parse_proposal_md(path: Path) -> dict[str, Any]:
    """Parse a single PROPOSAL.md into its constituent parts."""
    if not path.is_file():
        return {
            "valid": False,
            "issues": [f"PROPOSAL.md is missing: {path}"],
            "source_digest": "",
            "text": "",
            "frontmatter": {},
            "sections": {},
            "source_paths": [],
            "labels": [],
            "readiness": "",
            "declared_sources": [],
        }

    try:
        text = _read_utf8(path)
    except (OSError, UnicodeDecodeError) as exc:
        return {
            "valid": False,
            "issues": [f"unreadable PROPOSAL.md: {exc}"],
            "source_digest": "",
            "text": "",
            "frontmatter": {},
            "sections": {},
            "source_paths": [],
            "labels": [],
            "readiness": "",
            "declared_sources": [],
        }

    fm = _frontmatter(text)
    issues: list[str] = []

    sections: dict[str, str] = {}
    heading_order: list[str] = []
    toc_heading_order: list[str] = []
    current_heading: str | None = None
    current_lines: list[str] = []
    for line in text.splitlines():
        toc_heading = TOC_HEADING_RE.match(line)
        if toc_heading:
            depth = len(toc_heading.group(1))
            heading = (toc_heading.group(2) or "").strip()
            toc_heading_order.append(heading)
        else:
            depth = 0
            heading = ""
        if depth == 2:
            if current_heading is not None:
                sections[current_heading.strip().lower()] = "\n".join(current_lines)
            current_heading = heading
            heading_order.append(heading.lower())
            current_lines = []
        elif current_heading is not None:
            current_lines.append(line)
    if current_heading is not None:
        sections[current_heading.strip().lower()] = "\n".join(current_lines)

    for section in PROPOSAL_REQUIRED_SECTIONS:
        if section not in sections:
            issues.append(f"PROPOSAL.md missing required section: {section}")

    if len(heading_order) != len(set(heading_order)):
        issues.append("PROPOSAL.md contains duplicate H2 headings")

    positions = [heading_order.index(section) for section in PROPOSAL_REQUIRED_SECTIONS if section in heading_order]
    if len(positions) == len(PROPOSAL_REQUIRED_SECTIONS) and positions != sorted(positions):
        issues.append("PROPOSAL.md required sections are out of order")

    if "table of contents" in sections:
        toc_targets = [unquote(raw.strip()) for raw in LINK_RE.findall(sections["table of contents"])]
        expected_h2 = [
            f"#{_markdown_anchor(section)}"
            for section in heading_order
            if section != "table of contents"
        ]
        all_anchors = [
            f"#{_markdown_anchor(section)}"
            for section in toc_heading_order
            if section.lower() != "table of contents"
        ]
        h2_targets = [target for target in toc_targets if target in expected_h2]
        if (
            any(target not in all_anchors for target in toc_targets)
            or len(toc_targets) != len(set(toc_targets))
            or h2_targets != expected_h2
            or [all_anchors.index(target) for target in toc_targets]
            != sorted(all_anchors.index(target) for target in toc_targets)
        ):
            issues.append("PROPOSAL.md Table of Contents does not match H2 order")

    sources_text = sections.get("sources", "")
    source_paths: list[str] = []
    for target in _links(sources_text):
        candidate = (path.parent / target).resolve(strict=False)
        if _inside(candidate, path.parent) and candidate != path:
            source_paths.append(candidate.relative_to(path.parent).as_posix())

    required_frontmatter = (
        "title",
        "slug",
        "created",
        "created-at",
        "status",
        "readiness",
        "decision-owner",
        "source-documents",
    )
    for key in required_frontmatter:
        if key not in fm or fm.get(key) in (None, ""):
            issues.append(f"PROPOSAL.md frontmatter missing {key}")

    declared = fm.get("source-documents", [])
    normalized_declared: list[str] = []
    if not isinstance(declared, list) or not declared:
        issues.append("PROPOSAL.md source-documents must be a non-empty list")
    else:
        for source in declared:
            if not isinstance(source, str) or not source.strip():
                issues.append("PROPOSAL.md source-documents contains a non-string entry")
                continue
            raw_source_path = path.parent / source
            source_path = raw_source_path.resolve(strict=False)
            if not _inside(source_path, path.parent):
                issues.append(f"declared source is unsafe: {source}")
                continue
            normalized = source_path.relative_to(path.parent).as_posix()
            normalized_declared.append(normalized)
            if raw_source_path.is_symlink() or not source_path.is_file():
                issues.append(f"declared source is missing or not a regular file: {source}")

    if len(normalized_declared) != len(set(normalized_declared)):
        issues.append("PROPOSAL.md source-documents contains duplicate identities")
    if len(source_paths) != len(set(source_paths)):
        issues.append("PROPOSAL.md Sources contains duplicate internal identities")
    if sorted(normalized_declared) != sorted(source_paths):
        issues.append("PROPOSAL.md source-documents and Sources do not reconcile exactly")

    questions_text = sections.get("questions", "")
    labels = _unresolved_label_statements(questions_text)

    readiness = str(fm.get("readiness", ""))
    if readiness not in {"not-ready", "review-ready", "decision-ready"}:
        issues.append(f"PROPOSAL.md has invalid readiness: {readiness}")

    if not source_paths:
        issues.append("PROPOSAL.md Sources section has no copied source links")

    if re.search(r"\{\{[^{}]+\}\}|<!--[\s\S]*?-->", text):
        issues.append("PROPOSAL.md contains unresolved authoring scaffolding")

    legacy_names = {
        "implementation.md",
        "10-implementation.md",
        "11-supporting-sources.md",
        "INDEX.md",
        "metadata.md",
    }
    legacy = [
        child.name
        for child in path.parent.iterdir()
        if child.is_file() and (re.match(r"^0[1-9]-", child.name) or child.name in legacy_names)
    ]
    if legacy:
        issues.append(f"proposal workspace contains legacy authored files: {', '.join(sorted(legacy))}")

    valid = not issues
    source_digest = _text_digest(_canonical_json(source_paths))

    return {
        "valid": valid,
        "issues": issues,
        "source_digest": source_digest,
        "text": text,
        "frontmatter": fm,
        "sections": sections,
        "source_paths": source_paths,
        "labels": labels,
        "readiness": readiness,
        "declared_sources": normalized_declared,
    }


def _canonical_baseline(root: Path) -> tuple[bool, list[str], str]:
    """Validate the proposal baseline. Delegates to _parse_proposal_md."""
    parsed = _parse_proposal_md(root / "PROPOSAL.md")
    return parsed["valid"], parsed["issues"], parsed["source_digest"]


def _validate_supplied_manifest(root: Path, supplied: Any) -> list[str]:
    if isinstance(supplied, str):
        try:
            supplied = json.loads(_read_utf8(Path(supplied)))
        except (OSError, ValueError) as exc:
            return [f"cannot read supplied snapshot manifest: {exc}"]
    if isinstance(supplied, Mapping):
        supplied = [
            {"path": key, **(value if isinstance(value, Mapping) else {"sha256": value})}
            for key, value in supplied.items()
        ]
    if not isinstance(supplied, list):
        return ["snapshot manifest must be a list or path map"]
    actual: dict[str, dict[str, Any]] = {}
    for entry in _manifest_tree(root, "snapshot"):
        actual[entry["path"]] = entry
    issues: list[str] = []
    expected_paths: set[str] = set()
    for item in supplied:
        if not isinstance(item, Mapping) or not item.get("path") or not item.get("sha256"):
            issues.append("snapshot manifest contains an incomplete entry")
            continue
        path = str(item["path"])
        expected_paths.add(path)
        actual_entry = actual.get(path)
        if actual_entry is None:
            issues.append(f"snapshot manifest path is missing: {path}")
        elif str(item["sha256"]) != actual_entry["sha256"]:
            issues.append(f"snapshot manifest digest differs: {path}")
        if actual_entry is not None and (
            item.get("bytes") is not None
            and int(item["bytes"]) != actual_entry.get("bytes", -1)
        ):
            issues.append(f"snapshot manifest byte length differs: {path}")
    extra = sorted(set(actual) - expected_paths)
    issues.extend(f"snapshot manifest omits file: {path}" for path in extra)
    return issues


def _collect_default(cwd: Path) -> CollectorResult:
    captured = datetime.now(timezone.utc).isoformat()
    try:
        process = subprocess.run(
            COLLECTOR_ARGS,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError as exc:
        return CollectorResult(False, [], stderr=str(exc), returncode=127, cwd=str(cwd), captured_at=captured)
    stdout = process.stdout
    digest = hashlib.sha256(stdout.encode("utf-8")).hexdigest()
    if process.returncode != 0:
        return CollectorResult(False, [], stdout, process.stderr, process.returncode, str(cwd), captured, digest)
    try:
        value = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return CollectorResult(False, [], stdout, f"invalid JSON: {exc}", process.returncode, str(cwd), captured, digest)
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        return CollectorResult(False, [], stdout, "collector output is not an array of objects", process.returncode, str(cwd), captured, digest)
    return CollectorResult(True, value, stdout, process.stderr, process.returncode, str(cwd), captured, digest)


def _normalize_collector_result(value: Any, cwd: Path) -> CollectorResult:
    if isinstance(value, CollectorResult):
        return value
    if isinstance(value, list):
        serialized = json.dumps(value, sort_keys=True)
        return CollectorResult(True, value, serialized, cwd=str(cwd), captured_at=datetime.now(timezone.utc).isoformat(), output_digest=_text_digest(serialized))
    raise TypeError("collector_runner must return CollectorResult or list")


def _validate_collector(result: CollectorResult) -> list[str]:
    issues: list[str] = []
    names: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(result.records):
        location = f"collector[{index}]"
        for key in ("name", "class", "path", "selection"):
            if key not in item:
                issues.append(f"{location} lacks {key}")
        name = item.get("name")
        if not isinstance(name, str) or not name:
            continue
        if name in names:
            issues.append(f"duplicate collector winner {name}")
        names[name] = item
        if item.get("class") not in {"operation", "documentation"}:
            issues.append(f"{location} has an invalid class")
        path = Path(str(item.get("path", ""))).expanduser()
        if not path.is_file():
            issues.append(f"{location} path is unreadable: {path}")
    return issues


def _task_text(task: Mapping[str, Any]) -> str:
    values: list[str] = []
    for key in ("purpose", "context", "expectedOutput"):
        values.append(str(task.get(key, "")))
    values.extend(str(value) for value in task.get("filesToRead", []))
    values.extend(str(value) for value in task.get("filesToWrite", []))
    for item in task.get("executionInstructions", []):
        values.append(str(item))
    return " ".join(values)


def _load_tasks(plan: Path) -> tuple[Any, list[Diagnostic], bool]:
    path = plan / "tasks.json"
    if not path.exists():
        return None, [_diag("TA", "BLOCKED", "MISSING-PACKET", "tasks.json", "missing", "readable tasks.json", "atomicity cannot run", "tasks.json is required")], True
    try:
        value = json.loads(_read_utf8(path))
    except UnicodeDecodeError as exc:
        return None, [_diag("TA", "BLOCKED", "PACKET-READ", "tasks.json", str(exc), "UTF-8 JSON", "atomicity cannot run", "tasks.json is unreadable")], True
    except (OSError, json.JSONDecodeError) as exc:
        return None, [_diag("TA", "FAIL", "PACKET-SCHEMA", "tasks.json", str(exc), "schema-valid JSON", "published plan is invalid", "tasks.json cannot be parsed")], False
    try:
        process = subprocess.run(
            [
                "uv",
                "run",
                "--project",
                str(SCRIPTS_PROJECT),
                "validate-task-structure",
                "--state-file",
                str(path),
                "--schema",
                str(TASK_SCHEMA),
            ],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError as exc:
        return value, [
            _diag(
                "TA",
                "BLOCKED",
                "SCHEMA-VALIDATOR",
                "tasks.json",
                str(exc),
                "available shared task validator",
                "structural validity cannot be established",
                "shared task validator could not start",
            )
        ], True
    diagnostics: list[Diagnostic] = []
    if process.returncode == 0:
        return value, diagnostics, False
    try:
        payload = json.loads(process.stdout) if process.stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    messages = payload.get("errors") if isinstance(payload, Mapping) else None
    if not isinstance(messages, list) or not messages:
        messages = [process.stderr.strip() or process.stdout.strip() or "validator failed"]
    status = "FAIL" if process.returncode == 1 else "BLOCKED"
    criterion = "PACKET-SCHEMA" if status == "FAIL" else "SCHEMA-VALIDATOR"
    for message in messages[:20]:
        diagnostics.append(
            _diag(
                "TA",
                status,
                criterion,
                "tasks.json",
                str(message),
                "task-packet schema",
                "published plan structural validity is unavailable" if status == "BLOCKED" else "published plan is structurally invalid",
                str(message),
            )
        )
    return value, diagnostics, status == "BLOCKED"


def _proposal_check(inp: NormalizedInput, plan_text: str, tasks: Any, before: list[dict[str, Any]]) -> CheckResult:
    diagnostics: list[Diagnostic] = []
    criteria = [
        "decision traceability",
        "scope and exclusion traceability",
        "design-constraint traceability",
        "implementation-target traceability",
        "verification traceability",
        "source identity and labels",
        "write-boundary preservation",
    ]

    proposal_index = inp.proposal_root / "PROPOSAL.md"
    parsed = _parse_proposal_md(proposal_index)
    valid = parsed["valid"]
    issues = list(parsed["issues"])

    if inp.proposal_mode == "copied-snapshot":
        if inp.unavailable_reason is None or inp.copied_origin_identity is None or inp.copied_capture_time is None:
            issues.append("copied snapshot lacks provenance")
        try:
            issues.extend(_validate_supplied_manifest(inp.proposal_root, inp.copied_manifest))
        except AuditInputError as exc:
            issues.append(str(exc))

    if not valid or issues:
        for issue in sorted(set(issues)):
            diagnostics.append(
                _diag(
                    "PC",
                    "BLOCKED",
                    "BASELINE-COMPLETE",
                    "proposal baseline",
                    issue,
                    "complete readable baseline",
                    "proposal compliance evidence is unavailable",
                    issue,
                )
            )
        return CheckResult("Proposal compliance", "BLOCKED", "not observable", "HIGH", criteria, diagnostics, issues)

    proposal_text = parsed["text"]
    proposal_frontmatter = parsed["frontmatter"]
    proposal_sections = parsed["sections"]

    if tasks is None:
        diagnostics.append(
            _diag(
                "PC",
                "BLOCKED",
                "PLAN-PACKET",
                "plan/tasks.json",
                "unavailable",
                "readable tasks.json and tasks.md",
                "proposal-to-plan traceability cannot run",
                "the plan packet is unavailable",
            )
        )

    if not (inp.plan_workspace / "tasks.md").is_file():
        diagnostics.append(
            _diag(
                "PC",
                "FAIL",
                "PLAN-RENDERED",
                "plan/tasks.md",
                "missing",
                "rendered tasks.md",
                "the published plan is incomplete",
                "tasks.md is required and is never generated by the audit",
            )
        )

    if inp.comparison_snapshot:
        copy_issues: list[str] = []
        if not inp.comparison_origin_identity or not inp.comparison_capture_time or not inp.comparison_manifest:
            copy_issues.append("comparison snapshot lacks origin identity, capture time, or manifest")
        copy_valid, canonical_issues, _ = _canonical_baseline(inp.comparison_snapshot)
        copy_issues.extend(canonical_issues)
        if not copy_issues and copy_valid:
            try:
                copy_issues.extend(
                    _validate_supplied_manifest(
                        inp.comparison_snapshot, inp.comparison_manifest
                    )
                )
            except AuditInputError as exc:
                copy_issues.append(str(exc))
        if not copy_issues and copy_valid:
            authoritative = _manifest_tree(inp.proposal_root, "authoritative")
            copied = _manifest_tree(inp.comparison_snapshot, "copied-snapshot")
            left = {item["path"]: item["sha256"] for item in authoritative}
            right = {item["path"]: item["sha256"] for item in copied}
            for path in sorted(set(left) | set(right)):
                if left.get(path) != right.get(path):
                    observed = (
                        f"authoritative={left.get(path, 'missing')}; "
                        f"copied={right.get(path, 'missing')}"
                    )
                    diagnostics.append(
                        _diag(
                            "PC",
                            "FAIL",
                            "SOURCE-DRIFT",
                            path,
                            observed,
                            "identical baseline manifests",
                            "proposal compliance is not reproducible",
                            f"authoritative and copied proposal differ at {path}",
                        )
                    )
        if copy_issues:
            diagnostics.append(
                _diag(
                    "PC",
                    "BLOCKED",
                    "BASELINE-COMPLETE",
                    "comparison snapshot",
                    "; ".join(copy_issues),
                    "complete comparison snapshot",
                    "source comparison cannot run",
                    "comparison snapshot is incomplete",
                )
            )

    combined = plan_text + "\n" + "\n".join(
        _task_text(task) for task in (tasks.get("tasks", []) if isinstance(tasks, Mapping) else [])
    )
    lower = combined.lower()

    required_markers = {
        "decision traceability": ("recommendation", "selected direction", "recommend"),
        "scope and exclusion traceability": ("scope", "exclusion"),
        "design-constraint traceability": ("design constraint", "constraint"),
        "implementation-target traceability": ("implementation", "target"),
        "verification traceability": ("verification", "test", "acceptance"),
    }
    for criterion, markers in required_markers.items():
        if not any(marker in lower for marker in markers):
            diagnostics.append(
                _diag(
                    "PC",
                    "FAIL",
                    criterion.upper().replace(" ", "-"),
                    "plan tasks and brief",
                    "no trace marker",
                    "proposal material traceable to plan",
                    "proposal-derived scope is untraceable",
                    f"missing {criterion}",
                )
            )

    for statement in parsed["labels"]:
        if statement.lower() not in lower:
            diagnostics.append(
                _diag(
                    "PC",
                    "FAIL",
                    "LABEL-PRESERVATION",
                    statement,
                    "unresolved statement absent from plan",
                    statement,
                    "proposal uncertainty may be laundered",
                    f"lost proposal statement {statement}",
                )
            )

    source_paths = parsed["source_paths"]
    copied_paths = {path.relative_to(inp.plan_workspace).as_posix() for path in _tree_files(inp.plan_workspace)}
    for source in source_paths:
        if not any(Path(item).name == Path(source).name or source in item for item in copied_paths):
            diagnostics.append(
                _diag(
                    "PC",
                    "FAIL",
                    "SOURCE-COPY",
                    source,
                    "source absent from plan tree",
                    source,
                    "copied-source identity is not preserved",
                    f"proposal source {source} is not copied into the plan",
                )
            )

    for index, task in enumerate(tasks.get("tasks", []) if isinstance(tasks, Mapping) else []):
        for target in task.get("filesToWrite", []):
            target_text = str(target)
            if ".proposals" in target_text or target_text.rstrip("/").endswith("PROPOSAL.md"):
                diagnostics.append(
                    _diag(
                        "PC",
                        "FAIL",
                        "WRITE-BOUNDARY",
                        f"tasks[{index}].filesToWrite",
                        target_text,
                        "plan-owned targets only",
                        "audit cannot permit proposal mutation",
                        f"scope-expanding or proposal write target {target_text}",
                    )
                )

    plan_tokens = _significant_tokens(combined)

    impl_section = proposal_sections.get("implementation details", "")
    impl_stripped = impl_section.strip().lower()
    if impl_stripped and impl_stripped not in {"none", "none.", "n/a", "n/a."}:
        impl_tokens = _significant_tokens(impl_section)
        if impl_tokens and not impl_tokens.intersection(plan_tokens):
            diagnostics.append(
                _diag(
                    "PC",
                    "FAIL",
                    "IMPLEMENTATION-TRACEABILITY",
                    "PROPOSAL.md#implementation-details",
                    "no implementation terms in plan",
                    "implementation details traceable to plan tasks",
                    "implementation may be disconnected from plan",
                    "Implementation Details section terms are not found in plan",
                    "MEDIUM",
                )
            )

    verify_section = proposal_sections.get("verification criteria", "")
    verify_stripped = verify_section.strip().lower()
    if verify_stripped and verify_stripped not in {"none", "none.", "n/a", "n/a."}:
        verify_tokens = _significant_tokens(verify_section)
        if verify_tokens and not verify_tokens.intersection(plan_tokens):
            diagnostics.append(
                _diag(
                    "PC",
                    "FAIL",
                    "VERIFICATION-TRACEABILITY",
                    "PROPOSAL.md#verification-criteria",
                    "no verification terms in plan",
                    "verification criteria traceable to plan",
                    "verification may be disconnected from plan",
                    "Verification Criteria section terms are not found in plan",
                    "MEDIUM",
                )
            )

    readiness = str(proposal_frontmatter.get("readiness", ""))
    if readiness == "decision-ready":
        for label in parsed["labels"]:
            lower_label = label.lower()
            if lower_label.startswith("evidence gap:") and ("block" in lower_label or "blocks" in lower_label):
                diagnostics.append(
                    _diag(
                        "PC",
                        "FAIL",
                        "BLOCKING-RESEARCH",
                        label,
                        f"Evidence Gap blocks but readiness is {readiness}",
                        "blocking evidence gaps resolved before decision-ready",
                        "decision quality is compromised",
                        f"blocking Evidence Gap present with decision-ready readiness: {label}",
                    )
                )

    declared = parsed["declared_sources"]
    indexed = parsed["source_paths"]
    for src in declared:
        if src not in indexed:
            diagnostics.append(
                _diag(
                    "PC",
                    "WARNING",
                    "SOURCE-DRIFT",
                    "frontmatter source-documents",
                    f"declared: {src}",
                    "indexed in Sources section",
                    "source identity inconsistent",
                    f"source-documents entry {src} is not indexed in Sources",
                    "MEDIUM",
                )
            )

    return CheckResult("Proposal compliance", _disposition(diagnostics), "complete", "HIGH", criteria, diagnostics, [])


ACTION_VERBS = {
    "analyze", "assess", "audit", "build", "create", "delete", "design", "fix",
    "implement", "integrate", "migrate", "move", "remove", "rename", "replace",
    "review", "test", "update", "validate", "write",
}


def _clause_actions(text: str) -> list[set[str]]:
    clauses = re.split(r"\s+(?:and|then|while)\s+|[;]", text.lower())
    results: list[set[str]] = []
    for clause in clauses:
        actions: set[str] = set()
        for token in re.findall(r"[a-z]+", clause):
            for verb in ACTION_VERBS:
                stem = "analy" if verb == "analyze" else verb
                if token.startswith(stem):
                    actions.add(verb)
        results.append(actions)
    return results


def _result_boundaries(task: Mapping[str, Any]) -> int:
    expected = str(task.get("expectedOutput", ""))
    clauses = [
        clause
        for clause in re.split(r"\s+and\s+|[;,]", expected.lower())
        if len(_significant_tokens(clause)) >= 2
    ]
    write_roots = {
        "/".join(Path(str(target)).parts[:2])
        for target in task.get("filesToWrite", [])
        if str(target).strip()
    }
    return max(len(clauses), len(write_roots), 1)


def _valid_coupling(value: Any) -> bool:
    return isinstance(value, Mapping) and all(
        str(value.get(key, "")).strip()
        for key in ("rationale", "sharedResult", "verification")
    )


def _bounded_path_matches(pattern: str, candidate: str) -> bool:
    normalized_pattern = pattern.strip().strip("`").replace("\\", "/")
    normalized_candidate = candidate.strip().strip("`").replace("\\", "/")
    if not normalized_pattern or not normalized_candidate:
        return False
    if "**" in normalized_pattern:
        prefix = normalized_pattern.split("**", 1)[0].rstrip("/")
        return normalized_candidate == prefix or normalized_candidate.startswith(prefix + "/")
    if any(character in normalized_pattern for character in "*?["):
        return fnmatch.fnmatch(normalized_candidate, normalized_pattern)
    return normalized_candidate == normalized_pattern


def _atomicity_check(tasks: Any, schema_diagnostics: list[Diagnostic], schema_blocked: bool) -> CheckResult:
    criteria = ["published schema", "conceptual split test", "one purpose/result/verification boundary", "dependencies and predecessor reads", "coupling evidence"]
    if tasks is None:
        return CheckResult("Task atomicity", "BLOCKED", "not observable", "HIGH", criteria, schema_diagnostics, ["tasks.json is unavailable"])
    diagnostics = list(schema_diagnostics)
    if schema_diagnostics:
        diagnostics.append(_diag("TA", "NOT OBSERVABLE", "CONCEPTUAL-COVERAGE", "tasks.json", "schema invalid", "valid task packet", "conceptual atomicity cannot be independently evaluated", "conceptual review is not observable after schema failure"))
    task_list = tasks.get("tasks", []) if isinstance(tasks, Mapping) else []
    identities: dict[str, int] = {}
    for index, task in enumerate(task_list):
        task_key = str(task.get("taskId") or f"task-{index + 1}")
        if task_key in identities:
            diagnostics.append(_diag("TA", "FAIL", "DUPLICATE-IDENTITY", f"tasks[{index}]", task_key, "unique task identity", "task boundaries are ambiguous", f"duplicate task identity {task_key}"))
        identities[task_key] = index
        missing_optional = [key for key in ("taskId", "verification", "verificationCoverage", "antiPatternSignals", "purposeOutputAlignment") if key not in task]
        for key in missing_optional:
            diagnostics.append(_diag("TA", "WARNING", "OPTIONAL-METADATA", f"tasks[{index}].{key}", "omitted", "migration-compatible metadata when authoring evidence is available", "review confidence is reduced", f"optional metadata {key} is absent", "MEDIUM"))
        signals = [value for value in task.get("antiPatternSignals", []) if value != "none"]
        coupling = task.get("couplingRationale")
        if signals:
            diagnostics.append(_diag("TA", "FAIL", "COMPOUND-SIGNAL", f"tasks[{index}].antiPatternSignals", ", ".join(signals), "one independently reviewable concern", "task must be split or explicitly reconsidered by its owner", "declared compound-task signal requires boundary review"))
        purpose = str(task.get("purpose", ""))
        action_clauses = [actions for actions in _clause_actions(purpose) if actions]
        result_boundaries = _result_boundaries(task)
        if len(action_clauses) > 1 and result_boundaries > 1 and not _valid_coupling(coupling):
            diagnostics.append(_diag("TA", "FAIL", "SPLIT-TEST", f"tasks[{index}]", purpose, "one independently assignable, rejectable, retryable, completable, and verifiable result or explicit coupling evidence", "independently separable actions and results are merged", "purpose and expected output expose multiple uncoupled action boundaries"))
        elif len(action_clauses) > 1 and not _valid_coupling(coupling):
            diagnostics.append(_diag("TA", "WARNING", "SPLIT-HEURISTIC", f"tasks[{index}].purpose", purpose, "one independently reviewable concern", "multiple action clauses need semantic review", "purpose exposes multiple action clauses without coupling evidence", "MEDIUM"))
        alignment = task.get("purposeOutputAlignment")
        if isinstance(alignment, Mapping) and alignment.get("status") == "not-aligned":
            diagnostics.append(_diag("TA", "FAIL", "RESULT-ALIGNMENT", f"tasks[{index}].purposeOutputAlignment", str(alignment), "aligned purpose and expected output", "task result is not reviewable as stated", "purpose/output metadata declares misalignment"))
        if signals and not _valid_coupling(coupling):
            diagnostics.append(_diag("TA", "FAIL", "COUPLING-EVIDENCE", f"tasks[{index}]", "compound signal without couplingRationale", "one shared result and verification boundary with safety rationale", "merged concerns lack coupling evidence", "coupling evidence is required for a compound signal"))
    graph: dict[str, list[str]] = {key: [] for key in identities}
    for index, task in enumerate(task_list):
        current = str(task.get("taskId") or f"task-{index + 1}")
        for dependency in task.get("dependencies", []) or []:
            predecessor = str(dependency.get("taskId", "")) if isinstance(dependency, Mapping) else ""
            if predecessor not in identities or predecessor == current:
                diagnostics.append(_diag("TA", "FAIL", "DEPENDENCY-REFERENCE", f"tasks[{index}].dependencies", predecessor, "existing predecessor task", "dependency order is invalid", f"invalid dependency {predecessor}"))
                continue
            graph[current].append(predecessor)
            predecessor_task = task_list[identities[predecessor]]
            predecessor_outputs = [str(item) for item in predecessor_task.get("filesToWrite", [])]
            reads = [str(item) for item in task.get("filesToRead", [])]
            if predecessor_outputs and not any(
                _bounded_path_matches(output, read)
                for output in predecessor_outputs
                for read in reads
            ):
                diagnostics.append(_diag("TA", "FAIL", "PREDECESSOR-READ", f"tasks[{index}].filesToRead", ", ".join(reads), f"read predecessor {predecessor} artifact", "dependency input is not traceable", f"dependency {predecessor} lacks a predecessor read"))
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(node: str) -> None:
        if node in visiting:
            diagnostics.append(_diag("TA", "FAIL", "DEPENDENCY-CYCLE", node, "cycle", "acyclic dependency graph", "task order is not executable", f"dependency cycle includes {node}"))
            return
        if node in visited:
            return
        visiting.add(node)
        for predecessor in graph.get(node, []):
            visit(predecessor)
        visiting.remove(node)
        visited.add(node)
    for node in graph:
        visit(node)
    return CheckResult("Task atomicity", _disposition(diagnostics), "partial" if schema_diagnostics else "complete", "HIGH" if not diagnostics else "MEDIUM", criteria, diagnostics, [])


def _load_persisted_inventory(path: Path | None) -> tuple[list[dict[str, Any]] | None, str | None]:
    if path is None:
        return None, None
    try:
        value = json.loads(_read_utf8(path))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        return None, "persisted inventory is not an array of objects"
    return value, None


def _significant_tokens(value: Any) -> set[str]:
    tokens = set(re.findall(r"[a-z0-9]+", str(value).lower()))
    return {token for token in tokens if len(token) > 2 and token not in STOPWORDS}


def _profile_contract_fit(task: Mapping[str, Any], frontmatter: Mapping[str, Any]) -> tuple[bool, str]:
    selection = frontmatter.get("selection", {})
    if not isinstance(selection, Mapping):
        return False, "selection profile is missing"
    task_tokens = _significant_tokens(_task_text(task))
    evidence: list[str] = []
    tags = selection.get("tags", {})
    if isinstance(tags, Mapping):
        for group in ("actions", "inputs", "outputs", "topics"):
            values = tags.get(group, [])
            if not isinstance(values, list):
                continue
            for value in values:
                phrase_tokens = _significant_tokens(value)
                if phrase_tokens and phrase_tokens.issubset(task_tokens):
                    evidence.append(f"{group}:{value}")
    use_when = selection.get("use_when", [])
    if isinstance(use_when, list):
        for value in use_when:
            phrase_tokens = _significant_tokens(value)
            if phrase_tokens and len(phrase_tokens.intersection(task_tokens)) >= min(3, len(phrase_tokens)):
                evidence.append(f"use_when:{value}")
    return bool(evidence), "; ".join(evidence) if evidence else "no request-facing profile term matches the task"


def _skill_check(inp: NormalizedInput, tasks: Any, collector: CollectorResult, before: list[dict[str, Any]]) -> CheckResult:
    criteria = ["one-to-three cardinality", "fresh collector reconciliation", "winning name/class/path", "SKILL.md inspection", "contract fit and authority safety"]
    diagnostics: list[Diagnostic] = []
    if not collector.ok:
        diagnostics.append(_diag("SA", "BLOCKED", "COLLECTOR", "collector", collector.stderr or "collector failed", COLLECTOR_COMMAND, "skill assignment evidence is unavailable", "fresh collector run failed"))
        return CheckResult("Skill assignment", "BLOCKED", "not observable", "HIGH", criteria, diagnostics, ["fresh collector result unavailable"])
    collector_issues = _validate_collector(collector)
    for issue in collector_issues:
        diagnostics.append(_diag("SA", "BLOCKED", "COLLECTOR-OUTPUT", "collector", issue, "valid exact collector array", "skill assignment evidence is unreliable", issue))
    winners = {item.get("name"): item for item in collector.records if isinstance(item.get("name"), str)}
    passive = winners.get("task-contract")
    if passive is None or passive.get("class") != "documentation":
        diagnostics.append(_diag("SA", "BLOCKED", "PASSIVE-CONTEXT", "collector", str(passive), "task-contract documentation winner", "shared task semantics are unavailable as passive context", "task-contract was not reconciled from the fresh collector"))
    elif not Path(str(passive.get("path", ""))).expanduser().is_file():
        diagnostics.append(_diag("SA", "BLOCKED", "PASSIVE-CONTEXT", str(passive.get("path")), "unreadable", "readable task-contract SKILL.md", "shared task semantics are unavailable as passive context", "task-contract documentation cannot be read"))
    persisted, persisted_error = _load_persisted_inventory(inp.persisted_inventory)
    if persisted_error:
        diagnostics.append(_diag("SA", "WARNING", "HISTORICAL-INVENTORY", str(inp.persisted_inventory), persisted_error, "readable historical comparison", "current fresh authority remains usable", "persisted inventory comparison is unavailable", "MEDIUM"))
    if persisted is not None:
        old = {item.get("name"): item for item in persisted}
        for name, item in old.items():
            current = winners.get(name)
            if current and any(old.get(name, {}).get(key) != current.get(key) for key in ("class", "path")):
                diagnostics.append(_diag("SA", "FAIL", "HISTORICAL-WINNER-DRIFT", str(name), _canonical_json(item), _canonical_json(current), "selected assignment does not match the fresh winner", f"persisted winner differs for {name}"))
            elif current and _canonical_json(item) != _canonical_json(current):
                diagnostics.append(_diag("SA", "WARNING", "HISTORICAL-METADATA-DRIFT", str(name), _canonical_json(item), _canonical_json(current), "historical comparison differs without changing the winner", f"non-identity metadata drift for {name}", "MEDIUM"))
    if tasks is None:
        diagnostics.append(_diag("SA", "BLOCKED", "PACKET", "tasks.json", "unavailable", "readable task assignments", "skill assignment cannot run", "tasks.json is unavailable"))
        return CheckResult("Skill assignment", "BLOCKED", "not observable", "HIGH", criteria, diagnostics, ["tasks.json is unavailable"])
    for index, task in enumerate(tasks.get("tasks", []) if isinstance(tasks, Mapping) else []):
        skills = task.get("skills")
        location = f"tasks[{index}].skills"
        if not isinstance(skills, list) or not 1 <= len(skills) <= 3 or len(set(skills)) != len(skills):
            diagnostics.append(_diag("SA", "FAIL", "CARDINALITY", location, str(skills), "one to three unique names", "task assignment is invalid", "skill assignment cardinality or uniqueness is invalid"))
            continue
        operation_count = 0
        for name in skills:
            item = winners.get(name)
            if item is None:
                diagnostics.append(_diag("SA", "FAIL", "FRESH-PRESENCE", f"{location}.{name}", str(name), "exact name in fresh collector array", "no replacement or fallback is permitted", f"skill {name} is absent from the fresh collector"))
                continue
            path = Path(str(item.get("path", ""))).expanduser()
            try:
                text = _read_utf8(path)
                front = _frontmatter(text)
            except (OSError, UnicodeDecodeError) as exc:
                diagnostics.append(_diag("SA", "BLOCKED", "CONTRACT-READ", str(path), str(exc), "readable matching SKILL.md", "skill assignment cannot be verified", f"cannot inspect {name}"))
                continue
            if front.get("name") != name or front.get("class") != item.get("class"):
                diagnostics.append(_diag("SA", "FAIL", "WINNING-IDENTITY", str(path), _canonical_json({"name": front.get("name"), "class": front.get("class")}), _canonical_json({"name": name, "class": item.get("class")}), "selected skill identity is stale or substituted", f"SKILL.md identity does not match collector winner {name}"))
            selection = front.get("selection", {})
            if item.get("class") == "documentation":
                if not isinstance(selection, Mapping) or selection.get("role") != "reference":
                    diagnostics.append(_diag("SA", "FAIL", "PASSIVE-PROFILE", str(path), str(selection), "documentation profile with reference role", "passive context identity is invalid", f"documentation skill {name} lacks a passive reference profile"))
                continue
            if item.get("class") != "operation":
                diagnostics.append(_diag("SA", "FAIL", "AUTHORITY-SAFETY", f"{location}.{name}", str(item.get("class")), "operation owner or passive documentation", "unsupported class cannot own or support the task", f"skill {name} has an invalid task-assignment class"))
                continue
            operation_count += 1
            if not isinstance(selection, Mapping) or selection.get("role") != "owner":
                diagnostics.append(_diag("SA", "FAIL", "OWNER-PROFILE", str(path), str(selection), "operation profile with owner role", "task execution authority is invalid", f"operation skill {name} lacks an owner profile"))
                continue
            fits, fit_evidence = _profile_contract_fit(task, front)
            if not fits:
                diagnostics.append(_diag("SA", "FAIL", "CONTRACT-FIT", str(path), fit_evidence, "request-facing operation profile that matches the task", "the assigned operation does not own the requested result", f"operation skill {name} does not fit the task contract", "MEDIUM"))
        if operation_count == 0:
            diagnostics.append(_diag("SA", "FAIL", "EXECUTABLE-OWNER", location, str(skills), "at least one fitting operation owner", "passive documentation cannot execute the task", "task has no executable operation owner"))
    return CheckResult("Skill assignment", _disposition(diagnostics), "complete", "HIGH" if not diagnostics else "MEDIUM", criteria, diagnostics, [])


def _drift(before: list[dict[str, Any]], inp: NormalizedInput, collector: CollectorResult) -> list[Diagnostic]:
    after: list[dict[str, Any]] = []
    try:
        after.extend(_manifest_tree(inp.plan_workspace, "plan"))
        after.extend(_manifest_tree(inp.proposal_root, "proposal"))
        if inp.comparison_snapshot:
            after.extend(_manifest_tree(inp.comparison_snapshot, "comparison"))
        if inp.persisted_inventory:
            after.extend(_manifest_file(inp.persisted_inventory, "inventory"))
        for item in collector.records:
            path = Path(str(item.get("path", ""))).expanduser()
            if path.is_file():
                after.extend(_manifest_file(path, f"skill:{item.get('name', 'unknown')}"))
    except AuditInputError as exc:
        return [_diag("INTEGRITY", "BLOCKED", "MANIFEST-READ", "audited trees", str(exc), "stable readable inputs", "snapshot integrity cannot be established", "manifest verification failed")]
    left = _manifest_by_key(before)
    right = _manifest_by_key(after)
    diagnostics: list[Diagnostic] = []
    for key in sorted(set(left) | set(right)):
        if left.get(key, {}).get("sha256") != right.get(key, {}).get("sha256") or left.get(key, {}).get("bytes") != right.get(key, {}).get("bytes"):
            diagnostics.append(_diag("INTEGRITY", "BLOCKED", "INPUT-DRIFT", f"{key[0]}/{key[1]}", _canonical_json(right.get(key, {})), _canonical_json(left.get(key, {})), "affected audit checks are blocked", "input changed after the initial manifest"))
    return diagnostics


def _render_json_block(value: Any) -> str:
    return "```json\n" + json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n```"


def _render_diagnostics(diagnostics: list[Diagnostic]) -> str:
    if not diagnostics:
        return "- None."
    lines: list[str] = []
    for item in diagnostics:
        lines.extend(
            [
                f"- **{item.id}** — `{item.status}` — {item.message}",
                f"  - Criterion: `{item.criterion}`; location: `{item.location}`; confidence: `{item.confidence}`.",
                f"  - Expected: {item.expected}",
                f"  - Observed: {item.observed}",
                f"  - Impact: {item.impact}",
            ]
        )
    return "\n".join(lines)


def _render_check(check: CheckResult) -> str:
    evidence_lines = (
        [f"  - {gap}" for gap in check.evidence_gaps]
        if check.evidence_gaps
        else ["  - None."]
    )
    lines = [
        f"### Disposition: {check.disposition}",
        f"- Coverage: {check.coverage}",
        f"- Confidence: {check.confidence}",
        "- Criteria:",
        *[f"  - {criterion}" for criterion in check.criteria],
        "- Diagnostics:",
        _render_diagnostics(check.diagnostics),
        "- Evidence gaps:",
        *evidence_lines,
        "",
    ]
    return "\n".join(lines)


def _write_new_atomically(path: Path, content: str) -> None:
    data = content.encode("utf-8")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
        temporary.unlink()
    except FileExistsError as exc:
        raise AuditInputError("auditOutput appeared during audit; refusing overwrite") from exc
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def _render_report(inp: NormalizedInput, audit_id: str, overall: str, checks: list[CheckResult], manifest: list[dict[str, Any]], collector: CollectorResult, evidence_gaps: list[str], integrity: list[Diagnostic]) -> str:
    generated = datetime.now(timezone.utc).isoformat()
    proposal_metadata = {}
    proposal_index = inp.proposal_root / "PROPOSAL.md"
    if proposal_index.is_file():
        try:
            proposal_metadata = _frontmatter(_read_utf8(proposal_index))
        except (OSError, UnicodeDecodeError):
            proposal_metadata = {}
    plan_metadata = {}
    for candidate in ("PLAN.md", "README.md", "summary.md", "brief.md"):
        path = inp.plan_workspace / candidate
        if path.is_file():
            try:
                plan_metadata = _frontmatter(_read_utf8(path))
            except (OSError, UnicodeDecodeError):
                plan_metadata = {}
            if plan_metadata:
                break
    lines = [
        "# Plan Audit Report",
        "",
        "## Audit identity and input provenance",
        f"- Audit identity: `{audit_id}`",
        f"- Generated at: `{generated}` (provenance only; finding IDs do not contain this time)",
        f"- Plan workspace: `{inp.plan_workspace}`",
        f"- Proposal baseline: `{inp.proposal_root}`",
        f"- Baseline mode: `{inp.proposal_mode}`",
        f"- Proposal metadata (status/readiness/owner facts): {_render_json_block(proposal_metadata)}",
        f"- Plan metadata: {_render_json_block(plan_metadata)}",
        f"- Historical assignment inventory: `{inp.persisted_inventory or 'None'}` (comparison only)",
        f"- Copied-snapshot origin: `{inp.copied_origin_identity or 'None'}`; capture time: `{inp.copied_capture_time or 'None'}`",
        f"- Audit output: `{inp.audit_output}`",
        "- Read-only boundary: only the caller-declared new report may be written.",
        "- Input manifest:",
        _render_json_block(manifest),
        "- Fresh collector command:",
        f"  `{COLLECTOR_COMMAND}`",
        f"- Collector success: `{collector.ok}`; return code: `{collector.returncode}`; captured at: `{collector.captured_at}`",
        f"- Collector working directory: `{collector.cwd}`",
        f"- Collector configured project root: `{inp.workspace_root}`; config directory: `{Path.home() / '.config' / 'opencode'}`",
        f"- Collector output digest: `{collector.output_digest}`",
        "- Fresh collector array:",
        _render_json_block(collector.records),
        "",
        "## Overall disposition",
        f"- **{overall}**",
        "- Rollup precedence: `BLOCKED` > `FAIL` > `CONDITIONAL PASS` > `PASS`.",
        "- This disposition is audit evidence only; it is not approval, acceptance, readiness, implementation completion, or permission to repair.",
        "",
    ]
    for check in checks:
        lines.append(f"## {check.name}")
        if check.name == "Proposal compliance":
            lines.append("- Source comparison: authoritative baseline remains primary; see manifest and source-drift diagnostics.")
        if check.name == "Task atomicity":
            lines.append("- Structural and conceptual coverage are reported separately.")
        if check.name == "Skill assignment":
            lines.append("- Assignment authority: the one fresh exact operation/documentation collector array.")
        lines.append(_render_check(check))
    lines.extend(["## Evidence gaps and open decisions"])
    lines.extend(f"- {item}" for item in (evidence_gaps or ["None."]))
    lines.extend(["", "## Remediation handoff", "- Correction owner: `plan-writer`.", "- The auditor performed no correction, replacement assignment, publication, or self-certification."])
    remediation = [item for check in checks for item in check.diagnostics if item.status in {"FAIL", "BLOCKED", "WARNING"}]
    if remediation:
        lines.append("- Stable findings requiring bounded review:")
        for item in remediation:
            lines.append(f"  - `{item.id}` — revise only the plan-owned boundary identified by the finding, preserve sources and labels, then rerun this exact audit.")
    else:
        lines.append("- No remediation findings.")
    if integrity:
        lines.extend(["", "- Snapshot-integrity diagnostics:", _render_diagnostics(integrity)])
    return "\n".join(lines).rstrip() + "\n"


def audit(raw_input: Mapping[str, Any], *, workspace_root: Path | None = None, collector_runner: Callable[[Path], Any] | None = None, write_report: bool = True) -> AuditResult:
    """Run one audit and optionally create its one declared report."""
    inp = normalize_input(raw_input, workspace_root=workspace_root)
    collector = _normalize_collector_result((collector_runner or _collect_default)(inp.workspace_root), inp.workspace_root)
    roots = [(inp.plan_workspace, "plan"), (inp.proposal_root, "proposal")]
    if inp.comparison_snapshot:
        roots.append((inp.comparison_snapshot, "comparison"))
    if inp.persisted_inventory:
        roots.append((inp.persisted_inventory, "inventory"))
    for item in collector.records:
        path = Path(str(item.get("path", ""))).expanduser()
        if path.is_file():
            roots.append((path, f"skill:{item.get('name', 'unknown')}"))
    if any(_inside(inp.audit_output, root) for root, _ in roots):
        raise AuditInputError("auditOutput is inside a selected skill or other audited tree")
    manifest: list[dict[str, Any]] = []
    for root, label in roots:
        try:
            manifest.extend(_manifest_file(root, label))
        except AuditInputError as exc:
            manifest.append({"tree": label, "path": str(root), "error": str(exc)})
    manifest = sorted(manifest, key=lambda item: (item.get("tree", ""), item.get("path", "")))
    try:
        plan_text_parts = [_read_utf8(path) for path in _tree_files(inp.plan_workspace) if path.name.lower() in {"plan.md", "readme.md", "summary.md", "brief.md"}]
    except AuditInputError:
        plan_text_parts = []
    tasks, schema_diagnostics, schema_blocked = _load_tasks(inp.plan_workspace)
    proposal = _proposal_check(inp, "\n".join(plan_text_parts), tasks, manifest)
    atomicity = _atomicity_check(tasks, schema_diagnostics, schema_blocked)
    assignment = _skill_check(inp, tasks, collector, manifest)
    checks = [proposal, atomicity, assignment]
    integrity = _drift(manifest, inp, collector)
    if integrity:
        for check in checks:
            affected = check.name in {"Proposal compliance", "Task atomicity", "Skill assignment"}
            if affected:
                check.diagnostics.extend(integrity)
                check.disposition = "BLOCKED"
                check.coverage = "partial"
    overall = "BLOCKED" if integrity or any(check.disposition == "BLOCKED" for check in checks) else ("FAIL" if any(check.disposition == "FAIL" for check in checks) else ("CONDITIONAL PASS" if any(check.disposition == "CONDITIONAL PASS" for check in checks) else "PASS"))
    identity_material = {
        "plan": [(item.get("path"), item.get("sha256"), item.get("bytes")) for item in manifest if item.get("tree") == "plan"],
        "proposal": [(item.get("path"), item.get("sha256"), item.get("bytes")) for item in manifest if item.get("tree") == "proposal"],
        "collector": collector.records,
        "mode": inp.proposal_mode,
    }
    audit_id = "audit-" + _digest(identity_material)[:16]
    evidence_gaps = [gap for check in checks for gap in check.evidence_gaps]
    report = _render_report(inp, audit_id, overall, checks, manifest, collector, evidence_gaps, integrity)
    wrote = False
    if write_report:
        _write_new_atomically(inp.audit_output, report)
        wrote = True
    return AuditResult(audit_id, overall, inp.audit_output, report, checks, manifest, collector, wrote)


run_audit = audit


def _cli_input(args: argparse.Namespace) -> dict[str, Any]:
    baseline: dict[str, Any] = {"mode": args.baseline_mode, "root": args.proposal_baseline}
    if args.baseline_mode == "copied-snapshot":
        baseline.update({"unavailableReason": args.unavailable_reason, "originIdentity": args.origin_identity, "captureTime": args.capture_time, "manifest": args.snapshot_manifest})
    return {
        "planWorkspace": args.plan_workspace,
        "proposalBaseline": baseline,
        "assignmentInventory": args.assignment_inventory,
        "auditOutput": args.audit_output,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run one read-only plan audit")
    parser.add_argument("--plan-workspace", required=True)
    parser.add_argument("--proposal-baseline", required=True)
    parser.add_argument("--audit-output", required=True)
    parser.add_argument("--assignment-inventory")
    parser.add_argument("--baseline-mode", choices=["authoritative", "copied-snapshot"], default="authoritative")
    parser.add_argument("--unavailable-reason")
    parser.add_argument("--origin-identity")
    parser.add_argument("--capture-time")
    parser.add_argument("--snapshot-manifest")
    args = parser.parse_args(argv)
    try:
        result = audit(_cli_input(args))
    except (AuditInputError, OSError, ValueError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"auditId": result.audit_id, "overall": result.overall, "report": str(result.report_path)}))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
