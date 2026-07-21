# Worker Patterns for Orchestrated Skills

Reference for designing workers that receive delegation packets from orchestrated skills.
Workers are `class: delegated` skills that execute as stateless packet consumers within a pipeline.
See `./orchestration-usage.md` for how orchestrators dispatch workers.

## Worker Contract

Every worker receives an immutable delegation packet with these sections: `PURPOSE`, `DETAILS`, `FILES TO READ`, `FILES TO WRITE`, `SKILLS`, `EXECUTION INSTRUCTIONS`, `VERIFICATION`, `EXPECTED OUTPUT`.
Packet sections are authoritative operational directives — not suggestions.
Workers must not modify, add, or remove sections.
Workers preserve purpose, explicit prohibitions, write scope, named-skill scope, atomicity, and task-related discovery limits as hard boundaries.
Workers adapt supporting actions and execution order only when correctness requires it within those boundaries.

## Worker Patterns

### Stateless Worker

Reads input, produces output, retains no state between invocations.
Every invocation is independent — state is fully captured in input files and the delegation packet.
Idempotent by nature; safe for retry.

### Stateful Worker

Accumulates state across calls by writing intermediate files that subsequent invocations read.
Use for multi-pass tasks where later passes depend on earlier artifacts (incremental analysis, checkpoint-and-resume workflows).
**Risk**: Stale state if a prior invocation failed partially.
Orchestrators must clean state between runs or version files per run ID.

### Fan-Out Worker

A single worker cloned across multiple inputs.
The orchestrator decomposes a workload into sub-packets, then dispatches the same worker to each sub-packet in parallel.
Use when work units are independent and produce collatable results.
The orchestrator's `Decompose` step generates one packet per unit; concurrency limits live in the `Worker Strategy` section.
Each instance receives distinct `FILES TO WRITE` targets to avoid write conflicts.

### Verification Worker

A worker whose primary output is a verification result rather than a transformed artifact.
Use when verification logic is complex enough to merit a dedicated skill (compliance checking, schema validation, quality gates).
**Payload shape**: `"status": "pass"` or `"status": "fail"` with a `details` field under `Deliverable`.
The orchestrator reads this result in a `Verify` step and decides retry, skip, or escalate.

## Output Contract

Workers return a result envelope with `Worker Result`, `File Changes`, `Verification`, and `Deliverable` sections in that order.
The result status is `COMPLETE`, `PARTIAL`, or `BLOCKED`.
The `Deliverable` section preserves exactly what `EXPECTED OUTPUT` specifies.
For collated workflows, the payload under `Deliverable` conforms to `{status, source_tags, items}`.
See `./collation-format.md` for collation status values, source tag rules, and item schema guidance.
Workers write only to literal paths or bounded path patterns listed in `FILES TO WRITE` and report actual file outcomes in `File Changes`.

## Error Handling

Workers return `BLOCKED` status when a hard boundary or essential requirement prevents a usable deliverable.
Blocked envelopes state the blocker and unblock condition.
Workers return `PARTIAL` status when a usable deliverable exists but a non-critical instruction or verification check remains incomplete.
Orchestrators parse the envelope status before retrying, skipping, escalating, or collating the payload.
Orchestrators treat malformed envelopes as blocked inputs and never consume their payloads.
