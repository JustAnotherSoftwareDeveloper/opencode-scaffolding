# Feature With New Dependency

> **Authority boundary:** This is a passive workflow document. It describes a scoped
> practice for reference only; it is not an executable procedure or a source of
> execution authority.

`feature-with-new-dependency` - `python-project-writer`, `python-project-dependencies` -
Connect a dependency decision and authorized effects to a production behavior change.

**Use when:** A request asks for production behavior that depends on a package the
project does not already declare.

## Purpose

The dependency operation evaluates the missing capability and owns authorized package
effects; the production writer owns behavior and directly coupled regression tests.
The dependency decision is a prerequisite for dependent implementation, not an automatic
commitment to add the proposed package.

## Descriptive Sequence

1. **Capability Boundary** — The requested observable behavior and project contract
   identify the missing capability. Existing dependencies, standard-library options,
   project reuse, and supported Python/platform targets determine whether a new package
   is necessary at all.
2. **Dependency Decision And Effects** — The
   [dependency evaluation](dependency-evaluation.md) supplies API-fit, compatibility,
   maintenance/security, transitive-graph, authenticity, and license evidence. Add or
   replace identifies the authorized declaration, lock, and environment effects;
   no-add leaves a viable reuse alternative, while defer leaves the dependent work
   blocked on named evidence or a decision. A recommendation alone changes no state.
3. **Implementation Handoff** — The dependency report gives the writer the chosen
   capability, usable API/version assumptions, changed declarations, selected
   groups/extras, and resolution/environment results. Dependent implementation rests
   on that evidence once required effects are complete. The writer's production and
   directly coupled test changes preserve configuration and distribution boundaries.
4. **Behavior Evidence** — The writer's relevant configured tests and checks assess
   the requested behavior in the stated environment. The combined result preserves the
   distinction between dependency consistency and functional correctness, including
    failures or unsupported targets left unresolved by either outcome.

**Example handoff:** The dependency owner records `no-add` because an existing package
already supplies the needed capability, or records an authorized add with the selected
version/extra, metadata and lock diff, manager, and lock/sync result. Only after required
effects succeed does the writer implement against that API; a stale lock or unresolved
target compatibility is an explicit hold, not an assumed successful prerequisite.
Preserve an established manager rather than migrating merely to match a suggested
greenfield default. Keep runtime requirements in project dependencies, consumer-selectable
features in published extras, and development tools in dependency groups; groups are not
emitted as package metadata. A stale-lock check and an installed environment answer
different questions: for uv, `--locked` rejects stale metadata while `--frozen` skips the
freshness check. For the technical details and publisher citations, explicitly load
`python-project-reference -> reference/environment-and-dependencies.md`; distribution
ownership and consumer metadata are further explained in
`python-project-reference -> reference/distribution-artifacts.md`.

## Artifacts

- Project metadata (`pyproject.toml`, lock file, dependency groups) updated by the
  dependency operation only.
- Production source and directly coupled regression tests updated by the writer only.
- Dependency decision and handoff record with evidence links, API/version assumptions,
  unresolved risks, and rationale.

## Validation Context

- The dependency operation reports its decision, exact effect, and lock/sync validation.
- The writer reports changed paths, compatibility assumptions, and behavior/test results.
- Coverage or static-quality evidence is scoped to the actual changed targets, not a
  universal gate.

## Prerequisites

- A requested behavior and missing capability, with a candidate identity when supplied
  and enough project context to evaluate reuse or alternatives.
- Separate authorized scope for production/directly coupled test changes and any
  dependency effects; an evaluation-only request does not authorize implementation.
- Explicit authorization for dependency/environment effects before any write, install,
  lock update, or sync.
- The project's existing manager, lock, and supported-range context.

## Notes

- Incomplete material dependency evidence leaves dependent implementation deferred,
  with the missing evidence named. A no-add decision can still support a feature through
  an accepted reuse alternative.
- An evaluation-only request needs no production writer. Directly coupled feature
  tests need no separate test-writing operation by default.
- A dependency declaration does not create a distribution artifact; that outcome belongs
  to `python-package-distribution`.

## Operation Handoff

The consuming operation owns the imperative procedure and all execution decisions. It
translates this passive context into its own bounded steps and owns any tools, writes,
delegation, output, and completion validation. This document does not execute, call
tools, modify files, delegate work, load other skills transitively, grant authority, or
establish completion evidence. Any additional reference must be explicitly loaded by the
consuming operation.
