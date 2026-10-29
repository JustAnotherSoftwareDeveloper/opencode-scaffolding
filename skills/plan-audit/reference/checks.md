# Check Rules

## Proposal Compliance

Compare the proposal decision path with the plan brief, copied sources, task
contexts, reads, writes, dependencies, and verification. Check the selected
direction; scope and exclusions; design constraints; implementation targets;
verification criteria; source identity; and preservation of `Assumption:`,
`Evidence Gap:`, and `Open Question:` labels. Source drift, missing traceability,
changed source identity, scope-expanding writes, and lost labels fail. An
incomplete baseline blocks. If the workspace has no separate brief file, use
the root task-packet summary as the plan brief. A label is unresolved only when
it begins a labeled statement; prose that merely names the label syntax does
not create an unresolved item.

Validate that the PROPOSAL.md frontmatter `source-documents` list is consistent
with the `Sources` section links, every declared copied source is present as an
indexed file, and the frontmatter `readiness` state does not conflict with
blocking `Evidence Gap:` labels. A `decision-ready` proposal with an unresolved
blocking evidence gap fails. Source-drift checks compare authoritative and
copied-snapshot manifests byte-for-byte; any difference is a FAIL finding.

An explicit statement that a gap does not block the bounded decision is not
itself blocking research, even if the same gap blocks outcome claims. A separate
affirmative statement that it blocks the decision, readiness, or selection still
fails for `decision-ready`.

Traceability checks use these proposal heading names: `Recommendation`,
`Technical Rationale`, `Questions`, `Options Considered`, `Implementation
Details`, `Verification Criteria`, and `Sources`. Implementation traceability
validates that `Implementation Details` section terms appear in the plan;
verification traceability validates that `Verification Criteria` section terms
appear in the plan.

## Task Atomicity

Inspect the published packet against the shared task schema first. Separately
apply the task-contract split test with required predecessor outputs fixed and
available: independently assignable, rejectable, retryable, completable, or
verifiable results require separate tasks. Investigation that establishes
later scope, design, interfaces, or acceptance criteria is a predecessor
result. Each task has one purpose, one result, and one verification boundary.

Dependencies express order and require a predecessor read. Coupling requires
one shared result, one verification boundary, and evidence that separation
would be unsafe, misleading, or impossible. Schema failure fails structural
coverage and makes conceptual coverage unobservable. Declared compound signals
and independently separable results fail. Uncertain heuristics and omitted
migration-compatible metadata warn. Bounded predecessor writes match concrete
reads under the same path; glob syntax is not compared as a literal filename.

## Skill Assignment

Run the exact operation/documentation collector once. Every task has one to
three unique names, all present in that fresh array. Reconcile the
collector-winning name, class, and path; inspect the matching `SKILL.md`; and
require at least one request-fitting operation owner. Documentation entries
may accompany that owner as passive context when their profiles use the
reference role. Planning profiles cannot appear in the ordinary
operation/documentation assignment array. Collector failure, invalid output,
stale or unreadable winners, class/path mismatch, and missing contract fit
block or fail as specified.

The audit never chooses a replacement, repairs a stale path, reconstructs metadata,
or uses a persisted inventory as current authority.
