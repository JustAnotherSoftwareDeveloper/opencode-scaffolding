# Core Rules

Use these rules before assigning skills.

## Inventory Concerns

- List every question, change, operation, decision, and deliverable.
- Name the result produced by each concern.
- Do not use a workflow phase, shared topic, or desired packet size as a boundary.

## Split Aggressively

Create separate tasks when either concern can be assigned, rejected, retried,
completed, or verified without the other. Apply this test to analysis,
documentation, implementation, and operations.

Create as many tasks as the request requires. Do not target or cap task, file, step,
or skill counts.

## Keep One Result

Give each task one purpose and one expected result. Keep verification with the
result it checks. Create a separate verification task only when the user requests
an independently reviewable verification deliverable.

## Separate Dependencies

Represent dependent work as separate ordered tasks. Put the predecessor artifact
in the dependent task's `filesToRead`. A dependency explains order; it does not
prove that two concerns belong in one task.

## Require Coupling Evidence

Keep multiple concerns together only when all of these statements are true:

- They produce one shared result.
- They have one verification boundary.
- Separating execution, review, retry, or verification would be unsafe,
  misleading, or impossible.

Record that evidence in `couplingRationale`. Shared files, topics, releases,
destinations, skills, dependencies, or final documents are not sufficient evidence.

## Assign Skills Last

Stabilize task boundaries, results, verification, and dependencies before selecting
skills. Do not merge or split work to fit an available skill.

After any split or migration, revalidate boundaries, mappings, dependencies, and
skills. Treat uncertain language as a review prompt rather than proof of atomicity.
