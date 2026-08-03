# Generate Task JSON

The generator receives final direct-LLM assignments and the one frozen collector inventory.

## Required Inputs

- A schema-valid draft with final `skills` assignments.
- One bare-array inventory from the caller root.
- A safe output destination (`--output-dir` or `--output-file`).

## Generator-Owned Guarantees

- Validate inventory, names, classes, profiles, source roots, winning paths, and one-to-three cardinality.
- Preserve every supplied task field and skill order.
- Derive a safe destination and publish atomically without replacing an existing output.
- Emit no final output after invalid input, assignment mismatch, or publication failure.

The generator does not discover skills, select skills, score candidates, rerank, infer classes, or repair assignments. Selection and contract inspection belong to the workflow.
