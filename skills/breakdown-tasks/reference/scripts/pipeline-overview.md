# Pipeline Overview

Run both selection stages against one frozen inventory snapshot.

## Sequence

1. Preserve the caller root and collect the full inventory once.
2. Select and load every materially relevant planning profile directly, without a cap.
3. Produce a complete `{summary, tasks}` draft without `skills`.
4. Select one to three operation/documentation skills per task directly from the same snapshot.
5. Inspect winning task contracts and reconcile names, classes, paths, and cardinality.
6. Pass the draft, final assignments, and unchanged inventory to the generator.
7. Validate the packet without mutation or `--auto-fix`.

## Failure Rules

- No reranker, fallback, score, rank, threshold, or second collector call is permitted.
- Missing or irrelevant selection, path mismatch, contract mismatch, invalid assignment, or generator failure blocks.
- No task file or partial output is published after failure.
- Sources and all non-skill task fields remain unchanged.
