# Evaluation fixtures

The stable synthetic corpus is versioned in `qwen3_ollama_skill_ranking_eval.py`.
Real shadow inputs must be privacy-reviewed and stored as JSON Lines with one
record per packet: `packet_id`, `task` (redacted), `lexical_names`,
`adjudicated_names`, `reviewer_ids`, `adjudication_timestamp`, and
`privacy_review_id`. Do not add real packets until the owner approves retention,
access, and reviewer roles. The native harness accepts no real corpus by default.
