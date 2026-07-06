"""FlashRank-based skill assignment for breakdown-tasks decomposition.

Consumers: assign-skills CLI.

Renders skill metadata into structured text passages, uses a FlashRank
cross-encoder reranker to rank candidates against each task draft, and
selects skills by floor threshold.
"""
