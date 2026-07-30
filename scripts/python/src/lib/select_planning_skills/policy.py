"""Validated cardinality policy for passive planning-context selection.

The production values below are calibrated from the recorded planning benchmark,
not from executable task assignment.  The benchmark's nine no-match cases all
require an empty result, while the threshold boundary separates the highest
negative score (0.9139602032827805) from the lowest direct positive score
(0.9808757994493688) for both supported profiles.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

MAX_CARDINALITY = 3
SUPPORTED_MINIMUM_CARDINALITIES = (0, 1)
ORDERING_RULE = "descending score, then stable candidate order"
DecisionGate = Literal["benchmark-pending", "benchmark-approved"]

# Traceability: tests/fixtures/planning_skill_ranker/evaluation.json records
# q8/q4 exact-set and empty-result outcomes for cases.json.  The approved
# precision-first decision is threshold 0.95 with zero-to-three cardinality;
# multi-reference recall remains a documented benchmark follow-up, not a reason
# to lower the inclusion threshold.
PRODUCTION_ABSOLUTE_INCLUSION_THRESHOLD = 0.95
PRODUCTION_MINIMUM_CARDINALITY = 0
PRODUCTION_DECISION_GATE: DecisionGate = "benchmark-approved"


class PlanningSelectionConfigurationError(ValueError):
    """Raised when a planning selection policy is not safe to use."""


@dataclass(frozen=True, slots=True)
class PlanningSelectionPolicy:
    """Selector policy supplied by the selector's construction boundary.

    The defaults are the benchmark-approved production configuration.  Callers
    may still provide explicit values for controlled evaluation or alternate
    validated configurations.
    """

    absolute_inclusion_threshold: float = PRODUCTION_ABSOLUTE_INCLUSION_THRESHOLD
    minimum_cardinality: int = PRODUCTION_MINIMUM_CARDINALITY
    max_cardinality: int = MAX_CARDINALITY
    decision_gate: DecisionGate = PRODUCTION_DECISION_GATE

    def __post_init__(self) -> None:
        if (
            not isinstance(self.max_cardinality, int)
            or isinstance(self.max_cardinality, bool)
            or not 1 <= self.max_cardinality <= MAX_CARDINALITY
        ):
            raise PlanningSelectionConfigurationError(
                f"max_cardinality must be between one and {MAX_CARDINALITY}"
            )
        if (
            not isinstance(self.minimum_cardinality, int)
            or isinstance(self.minimum_cardinality, bool)
            or self.minimum_cardinality not in SUPPORTED_MINIMUM_CARDINALITIES
            or self.minimum_cardinality > self.max_cardinality
        ):
            raise PlanningSelectionConfigurationError(
                "minimum_cardinality must be zero or one and no greater than "
                "max_cardinality"
            )
        if (
            not isinstance(self.absolute_inclusion_threshold, (int, float))
            or isinstance(self.absolute_inclusion_threshold, bool)
            or not math.isfinite(self.absolute_inclusion_threshold)
            or not 0 <= self.absolute_inclusion_threshold <= 1
        ):
            raise PlanningSelectionConfigurationError(
                "absolute_inclusion_threshold must be a finite probability"
            )
        if self.decision_gate not in ("benchmark-pending", "benchmark-approved"):
            raise PlanningSelectionConfigurationError(
                "decision_gate must be benchmark-pending or benchmark-approved"
            )

    @property
    def production_approved(self) -> bool:
        """Whether benchmark evidence has explicitly cleared this policy."""

        return self.decision_gate == "benchmark-approved"


def stable_order_key(score: float, candidate_index: int) -> tuple[float, int]:
    """Return the deterministic ordering key required by the proposal.

    The caller performs scoring; this helper only expresses descending-score,
    original-candidate-order tie breaking.
    """

    if not math.isfinite(score) or not 0 <= score <= 1:
        raise PlanningSelectionConfigurationError("score must be a finite probability")
    if (
        not isinstance(candidate_index, int)
        or isinstance(candidate_index, bool)
        or candidate_index < 0
    ):
        raise PlanningSelectionConfigurationError(
            "candidate_index must be a non-negative integer"
        )
    return (-score, candidate_index)


__all__ = [
    "DecisionGate",
    "MAX_CARDINALITY",
    "ORDERING_RULE",
    "PRODUCTION_ABSOLUTE_INCLUSION_THRESHOLD",
    "PRODUCTION_DECISION_GATE",
    "PRODUCTION_MINIMUM_CARDINALITY",
    "PlanningSelectionConfigurationError",
    "PlanningSelectionPolicy",
    "SUPPORTED_MINIMUM_CARDINALITIES",
    "stable_order_key",
]
