# Check Rules

## Proposal Compliance

Compare the proposal decision path with the plan brief, copied sources, task
contexts, reads, writes, dependencies, and verification. Check selected direction,
scope and exclusions, design constraints, implementation targets, acceptance tests,
source identity, and preservation of `Assumption:`, `Evidence Gap:`, and
`Open Question:` labels. Source drift, missing traceability, changed source identity,
scope-expanding writes, and lost labels fail. An incomplete baseline blocks.
The root task-packet summary is the plan brief when the workspace has no separate
brief file. A label is unresolved only when it begins a labeled statement; prose that
merely names the label syntax does not create an unresolved item.

## Task Atomicity

First inspect the published packet against the shared task schema. Separately apply
the task-contract split test: independently assignable, rejectable, retryable,
completable, or verifiable concerns require separate tasks. A task has one purpose,
one result, and one verification boundary. Dependencies express order and require a
predecessor read; coupling requires one shared result, one verification boundary,
and evidence that separation would be unsafe, misleading, or impossible. Schema
failure fails structural coverage and makes conceptual coverage not observable.
Declared compound signals and independently separable results fail. Uncertain
heuristics and omitted migration-compatible metadata warn.
Bounded predecessor writes match concrete reads under the same path; glob syntax is
not compared as a literal filename.

## Skill Assignment

Run the exact operation/documentation collector once. Every task has one to three
unique names that are present in that fresh array. Reconcile the collector-winning
name, class, and path, inspect the matching `SKILL.md`, and require at least one
request-fitting operation owner. Documentation entries may accompany that owner as
passive context when their profiles use the reference role. Planning profiles cannot
appear in the ordinary operation/documentation assignment array. Collector failure,
invalid output, stale or unreadable
winners, class/path mismatch, and missing contract fit block or fail as specified.

The audit never chooses a replacement, repairs a stale path, reconstructs metadata,
or uses a persisted inventory as current authority.
