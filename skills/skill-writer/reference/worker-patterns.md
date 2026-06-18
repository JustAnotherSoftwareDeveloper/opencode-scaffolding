# Worker Patterns for Orchestrated Skills

Reference for designing workers that receive delegation packets from orchestrated skills.
Workers are `class: delegated` skills that execute autonomously within a pipeline.
See `./orchestrated-usage.md` for how orchestrators dispatch workers and `../REFERENCE.md` for class taxonomy.

## Worker Contract

Every worker receives an immutable delegation packet with these sections: `PURPOSE`, `DETAILS`, `FILES TO READ`, `FILES TO WRITE`, `SKILLS`, `EXECUTION INSTRUCTIONS`, `VERIFICATION`, `EXPECTED OUTPUT`.
Workers must not modify, add, or remove sections.

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
**Output shape**: `"status": "pass"` or `"status": "fail"` with a `details` field.
The orchestrator reads this result in a `Verify` step and decides retry, skip, or escalate.

## Output Contract

Workers produce exactly what `EXPECTED OUTPUT` specifies.
Default format is plaintext unless the packet requires JSON.
For collated workflows, JSON must conform to `{status, source_tags, items}`.
See `./collation-reference.md` for status values, source tag rules, and item schema guidance.
Workers write only to files listed in `FILES TO WRITE`.

## Error Handling

Workers report `BLOCKED: <reason>` on failure — orchestrators handle retry, skip, or escalate.
Failure reasons include missing `FILES TO READ`, contradictory instructions, or step execution failure.
Workers must not silently swallow errors; stop and report the blocker immediately.