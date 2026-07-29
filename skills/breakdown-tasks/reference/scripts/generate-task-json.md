# Generate Task JSON

Run `generate-task-json` with standard-input drafts and a frozen skill inventory.

## Required Inputs

- Pass `--skills-file` with one bare collector array.
- Pass `--project-root` with the preserved caller root.
- Pass either `--output-dir` or `--output-file`.
- Provide one schema-valid `TaskDraftList` on standard input.

## Assignment Modes

- Use `--assignment-mode qwen` for authoritative checked-model assignment.
- Use `--assignment-mode shadow` with `--diagnostics-file` for comparison.
- Use `--assignment-mode lexical` for rollback without model initialization.
- Select Q4 only through `--model-profile q4`.
- Keep Q8 as the default checked profile.

## Exit Codes

- Exit `0` after atomic output publication and print the relative path.
- Exit `1` for manifest, model, transport, scoring, diagnostics, or output failures.
- Exit `2` for JSON, schema, inventory, token-budget, path, or argument failures.

## Guarantees

- Validate drafts and inventory before model initialization.
- Reject oversized complete pairs before HTTP access.
- Restrict normal model access to loopback Ollama.
- Preserve non-skill task fields.
- Validate final output before publication.
- Never replace an existing task or diagnostics file.
