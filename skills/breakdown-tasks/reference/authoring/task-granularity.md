# Task Granularity Guidelines

These are authoring guidance for choosing boundaries before skills are assigned.

## Default and exception

Use one task per conceptual change and treat one file per task as a review heuristic,
not a universal rule. A tightly coupled multi-file change is valid when the files
jointly produce one result with one verification signal. Record the shared outcome,
why separate execution would be misleading, and the exact verification evidence.
Never use this exception for implementation plus tests, analysis plus planning, or
unrelated changes.

## Purpose/output alignment

Use one action verb in one purpose sentence and one `expectedOutput` paragraph. The
output must be the result of that purpose, while verification names observable
evidence for the same result. A file write and a test result are two outputs; keep
production and testing in separate tasks.

## Pipeline and dependencies

Split independent concerns and parallelize them. Keep dependent concerns
sequential, naming the prior output in `filesToRead`. In this workflow, candidate
decomposition is first; skill assignment follows it. The first task establishes
shared outputs that subsequent dependent tasks list in `filesToRead`.

Do not use lifecycle stages such as analysis, proposal, implementation, or review as
automatic task boundaries. A stage may contain many independent questions or
changes, each requiring its own task. Conversely, do not add a stage the request did
not ask for.

## Split test and revalidation

There is no task-count ceiling or target. Before publication, ask whether any clause
of a task can be completed, rejected, retried, assigned, or verified independently.
If yes, split it. Apply this test to analytical dimensions as well as file changes:
architecture taxonomy, style conformance, workflow policy, migration, and validation
are separate questions unless evidence proves one indivisible result. After splitting
or migrating a concern, re-check every new boundary, purpose, expected output,
verification, dependency, and assigned skill. Keep the one-to-three skills-per-task
constraint unchanged.
