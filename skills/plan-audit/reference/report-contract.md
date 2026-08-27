# Report Contract

The report is one UTF-8 Markdown file with these semantic sections, in order:

1. **Audit identity and input provenance** — deterministic audit identity, resolved
   inputs, baseline mode, metadata facts, read-only boundary, complete SHA-256
   manifest, and the fresh collector command, provenance, digest, and array.
2. **Overall disposition** — the rollup independent of proposal status, readiness,
   acceptance, implementation completion, or approval.
3. **Proposal compliance** — coverage, confidence, traceability criteria, source
   comparison, diagnostics, and evidence gaps.
4. **Task atomicity** — structural/schema coverage, conceptual split-test coverage,
   dependency and coupling evidence, diagnostics, and evidence gaps.
5. **Skill assignment** — cardinality, exact fresh-winner reconciliation, inspected
   contracts, contract fit, authority safety, and diagnostics.
6. **Evidence gaps and open decisions** — unavailable, ambiguous, or explicitly
   unresolved evidence without resolving it.
7. **Remediation handoff** — stable finding IDs, bounded plan-owned target,
   correction owner `plan-writer`, and the fresh-audit condition.

Every diagnostic includes its stable ID, status, criterion, location, observed and
expected evidence, impact, and confidence. Diagnostic statuses may be `WARNING`,
`NOT OBSERVABLE`, or `BLOCKED` in addition to the four check dispositions.

`PASS` means that all applicable evidence ran without a warning or violation. A
`CONDITIONAL PASS` has only a non-blocking warning or optional non-observable
criterion. `FAIL` has stable observable contract violations. `BLOCKED` lacks stable
evidence or detected input integrity. Overall precedence is `BLOCKED`, `FAIL`,
`CONDITIONAL PASS`, then `PASS`.

The report is evidence, not approval, acceptance, readiness, implementation
completion, or permission to repair.
