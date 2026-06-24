# Dependency Patterns

Common dependency topologies for task graphs and per-task dependency mapping.
Each node represents a task ID.
Arrows indicate "depends on" relationships.

## Sequential Chain

Tasks execute one after another, each depending on the previous.
`1 → 2 → 3`
Task 2 depends on task 1.
Task 3 depends on task 2.
No parallelism possible.

**Use case:** Build a feature in layers — create model, add routes, wire tests.

## Fan-Out

One task produces output consumed by multiple parallel downstream tasks.
`1 → 2, 1 → 3, 1 → 4`
Tasks 2, 3, and 4 each depend on task 1.
Tasks 2, 3, and 4 can execute in parallel after task 1 completes.

**Use case:** Generate a schema, then independently scaffold model, validator, and type definitions.

## Fan-In

Multiple parallel tasks converge into a single downstream task.
`1 → 3, 2 → 3`
Task 3 depends on both task 1 and task 2.
Tasks 1 and 2 can execute in parallel.
Task 3 waits for both to complete.

**Use case:** Independently refactor two modules, then update integration tests that cover both.

## Parallel

Multiple tasks with no dependencies between them.
All execute concurrently.
`1, 2, 3`
No task depends on any other.
All three execute in parallel.

**Use case:** Lint, type-check, and build — independent verification steps.

## Per-Task Dependency Mapping

Populate each task's `dependencies` array with UUID v4 references to prerequisite tasks.
This per-task approach enables precise dependency tracking without a separate root-level map.

- **Sequential chain**: Task B depends on A, Task C depends on B.
  Task B: `"dependencies": ["<uuid-of-A>"]`
  Task C: `"dependencies": ["<uuid-of-B>"]`
- **Fan-out**: One task produces output consumed by multiple downstream tasks.
  Task B: `"dependencies": ["<uuid-of-A>"]`
  Task C: `"dependencies": ["<uuid-of-A>"]`
- **Fan-in**: Multiple tasks must complete before a downstream task can begin.
  Task C: `"dependencies": ["<uuid-of-A>", "<uuid-of-B>"]`
- **Parallel**: Tasks with empty `dependencies` arrays have no prerequisites.
  Task A: `"dependencies": []`
  Task B: `"dependencies": []`

### Validation

Every UUID in a `dependencies` array must reference a task in the same decomposition.
The dependency graph must be acyclic (no circular dependencies).
Dependencies reference tasks by UUID, never by array position or sequential number.