"""Stable prompt contract for passive planning-context relevance."""

PLANNING_RENDER_VERSION = "planning-request-v1"
PLANNING_PROMPT_VERSION = "qwen3-reranker-4b-classifier-planning-v1"
PLANNING_INSTRUCTION = (
    "Determine whether this class planning reference provides materially useful "
    "passive context for decomposing the supplied request. Generic planning "
    "relevance is not sufficient; answer yes only when the reference materially "
    "informs that decomposition."
)
