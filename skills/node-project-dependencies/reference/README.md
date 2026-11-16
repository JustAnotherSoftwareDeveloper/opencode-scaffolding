# Dependency And Environment Reference

This reference supports the `node-project-dependencies` operation in TypeScript
Node.js and Bun projects and is an index, not another workflow: the
[`node-project-dependencies` entrypoint](../SKILL.md) owns routing, input
normalization, the decision procedure, authorization checks, validation, and
reporting. The index routes two reader questions and states the limits that apply
to both.

## Routes By Question

### Evaluation And Authorized Change

**How do I connect a candidate to a concrete need and bound an authorized change?**
The answer is [Evaluation And Environment Changes](evaluation-and-environment-changes.md).
The discriminating clue is that the request decides whether a dependency or
environment change belongs at all: it weighs a candidate against the need, chooses
no-add, add, replace, or defer, and names the effects an authorization covers. The
page owns the decision and authorization question; manager mechanics are evidence it
consults, not its subject.

### Manager Behavior For A Selected Version

**For this manager and version, how do dependency groups, peers, optional
dependencies, workspaces, locks, and install effects behave?**
The answer is [Manager Semantics And Workspace Placement](manager-semantics-and-workspace-placement.md).
The discriminating clue is that the request turns on recorded manager behavior — a
dependency group, peer or optional role, workspace linking rule, lock record, or
command effect — rather than on whether the dependency is justified. The page states
publisher-documented behavior for the named manager and version, not a default or a
recommendation.

A route names where an answer lives. It grants no operation, tool, edit, approval, or
completion authority, and it creates no delegation or required sequence.

## Keep Evidence Layers Distinct

Declarations, selected tools, the resolved graph, and installed state are separate
layers, and one does not prove another. A declaration records intended dependency
state; a selected runtime or package manager records a dispatch choice; a lockfile
records one manager's resolved graph; installed state is the physical layout that
resulted. Each question is answered from its own layer, and none substitutes for
another.

## Read-Only Limit

Evaluation is read-only unless the request explicitly authorizes a concrete change. A
recommendation does not authorize installation, lockfile edits, manager or runtime
migration, or environment synchronization. Missing policy or approval decisions are
escalated rather than invented.

## Limits

This reference does not set organization-wide security or legal policy, prescribe a
migration, define a universal toolchain, select a manager or runtime, or establish a
Vite workflow. No statement here is a universal version or manager rule. An incidental
transitive package edge is neither prohibited nor proof that a dependency is absent. It
does not transfer this repository's `scripts/node/` utilities or their Bun conventions
to an application, and no page here grants an operation, tool, edit, approval, or
completion authority.
