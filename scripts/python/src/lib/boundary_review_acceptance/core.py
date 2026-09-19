"""Deterministic eligibility checks for delegator boundary-review acceptance.

This module deliberately checks *eligibility*, not semantic atomicity.  A caller
supplies the original request and an explicit supervisory attestation after its
request-aware review.  The canonical packet must first pass structural validation;
that result establishes only that the boundary-review interface is usable.
"""

from __future__ import annotations

from typing import Any

from lib.validate_task_structure.core import validate


def accept_boundary_review(
    original_request: Any,
    packet: Any,
    review_evidence: Any,
    schema: dict[str, Any],
) -> tuple[bool, list[str]]:
    """Return whether a packet is eligible for downstream display or dispatch.

    ``review_evidence`` is an explicit supervisory attestation with exactly these
    fields:

    * ``reviewedRequest``: the unchanged original request;
    * ``packetSlug``: the canonical packet slug reviewed;
    * ``reviewedTaskIds``: every final packet task ID, once;
    * ``disposition``: ``"accepted"`` only when the review substantiates the
      boundaries;
    * ``rationale``: non-empty reviewer rationale; and
    * ``deficiencies``: an empty list.  Any identified deficiency rejects the
      packet and must be handled by focused re-decomposition.

    The function does not infer whether prose is atomic, use task/file counts as a
    proxy, or transform a structurally valid packet into semantic approval.
    """
    diagnostics: list[str] = []
    if not isinstance(original_request, str) or not original_request.strip():
        diagnostics.append("original request must be a non-empty string")

    structural_valid, structural_diagnostics = validate(packet, schema)
    if not structural_valid:
        diagnostics.append("canonical packet failed structural validation")
        diagnostics.extend(structural_diagnostics)
        return False, diagnostics

    assert isinstance(packet, dict)
    tasks = packet["tasks"]
    assert isinstance(tasks, list)
    task_ids = [task["taskId"] for task in tasks if isinstance(task, dict)]

    if not isinstance(review_evidence, dict):
        diagnostics.append("explicit review evidence must be an object")
        return False, diagnostics

    if review_evidence.get("reviewedRequest") != original_request:
        diagnostics.append("review evidence must bind the unchanged original request")
    if review_evidence.get("packetSlug") != packet["slug"]:
        diagnostics.append("review evidence must bind the canonical packet slug")

    reviewed_task_ids = review_evidence.get("reviewedTaskIds")
    if not _same_unique_task_ids(reviewed_task_ids, task_ids):
        diagnostics.append(
            "review evidence must cover each final packet taskId exactly once"
        )
    if review_evidence.get("disposition") != "accepted":
        diagnostics.append("review evidence disposition must be 'accepted'")
    if not isinstance(review_evidence.get("rationale"), str) or not review_evidence[
        "rationale"
    ].strip():
        diagnostics.append("review evidence must include a non-empty rationale")

    deficiencies = review_evidence.get("deficiencies")
    if not isinstance(deficiencies, list):
        diagnostics.append("review evidence must include a deficiencies list")
    elif deficiencies:
        diagnostics.append("review evidence identifies unresolved deficiencies")

    return not diagnostics, diagnostics


def _same_unique_task_ids(value: Any, task_ids: list[str]) -> bool:
    """Return whether *value* is the exact, duplicate-free final task ID set."""
    return (
        isinstance(value, list)
        and all(isinstance(task_id, str) for task_id in value)
        and len(value) == len(set(value))
        and set(value) == set(task_ids)
    )
