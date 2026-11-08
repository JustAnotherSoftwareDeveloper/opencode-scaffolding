# Dependency Evaluation

> **Authority boundary:** This is a passive workflow document. It describes a scoped
> practice for reference only; it is not an executable procedure or a source of
> execution authority.

`dependency-evaluation` - `python-project-dependencies` - Decide add/no-add/replace/defer
for a candidate package and apply authorized declaration, lock, or environment effects.

**Use when:** A request asks whether a Python project should add, remove, replace, or
defer a dependency, or asks to change dependency declarations, resolution, lock, or
sync state.

## Purpose

This practice distinguishes an evidence-based dependency decision from permission
to change project state. `python-project-dependencies` owns both outcomes when
requested, preserving the project's manager, compatibility promises, and dependency
roles without implementing production behavior or building distributions.

## Descriptive Sequence

1. **Need And Existing State** — A concrete capability or environment problem frames
   the evaluation. Standard-library and project reuse, manager/version, declarations,
   groups, extras, lock, and supported Python/platform constraints establish the baseline.
   Declared requirements, the resolved graph, and installed state are separate facts.
2. **Candidate Evidence And Decision** — Proportionate evidence covers API fit,
   supported targets, maintenance and security response, direct/transitive dependencies,
   source authenticity, build/install requirements, and licenses for the intended use.
   The operation's no-add/add/replace/defer decision records rationale and evidence gaps;
   popularity, activity, badges, and aggregate scores are clues, not verdicts.
3. **Authorized State Change** — Evaluation-only work ends with the decision record.
   When separately authorized, declaration, resolution, lock, or environment effects
   follow the existing manager's documented workflow and preserve dependency roles.
   A removal or replacement has an explicit affected-package scope; it is not implied
   by a recommendation. The resulting diff and graph show the actual effect.
4. **Consistency Evidence** — A manager-supported lock-currentness result, authorized
   sync outcome, or requested project check assesses the stated target and selected
   groups/extras. The report separates metadata consistency, installed state, and
    application behavior rather than treating one successful check as proof of all three.

**Example handoff:** A decision record identifies the capability and reuse alternatives,
candidate/source identity, target Python/platforms, direct and transitive graph, evidence
for maintenance/security/license questions, and reasons to add, decline, replace, or
defer. A recommendation ends evaluation-only work; if effects were authorized, report
the exact declaration/lock/environment diff and non-rewriting consistency result. Do not
convert signals such as popularity, release recency, badges, or aggregate scores into a
numeric verdict. Check the candidate's identity/source, capability fit, supported
Python/platforms, maintenance and vulnerability response, direct and transitive graph,
build/install behavior, and license evidence for the intended use. Separate the selected
runtime/group/extra from build-time dependencies: the visible graph may differ by target
and build environment. Missing material evidence is a named gap, not a pass. For detailed
dependency-group, graph, licensing, and manager-specific examples with publisher sources,
explicitly load `python-project-reference -> reference/environment-and-dependencies.md`.

## Artifacts

- Dependency decision record with need, candidate/source identity, dated evidence
  links, rationale, unresolved risks, and any responsible approval owner.
- Updated `pyproject.toml`, lock file, or environment only when explicitly authorized.
- Validation report with exact manager/version, targets, and results.

## Validation Context

- A non-rewriting lock-currentness check that tests metadata consistency, rather than
  merely trusting an existing lock; sync evidence only when that effect was authorized.
- The actual resolved graph and selected groups/extras for the stated targets.
- Any requested project checks run in the resolved environment.

## Prerequisites

- A named capability, candidate, removal scope, or environment problem sufficient to
  bound the requested evaluation or change.
- Explicit authorization for dependency/environment effects before any write, install,
  lock update, or sync.
- The project's existing manager, lock, groups, and supported-range context.

## Notes

- No-add and defer are useful outcomes; absent material evidence or authorization can
  leave the project unchanged without turning the recommendation into a failed install.
- An established manager is not migrated to match a proposed default. A successful
  local sync proves neither every supported target nor complete security/legal fitness.
- A dependency declaration is not a distribution artifact; artifact work belongs to
  `python-package-distribution`.
- Legal, security, and license questions that exceed the project's evidence scope need
  escalation to the responsible owner.

## Operation Handoff

The consuming operation owns the imperative procedure and all execution decisions. It
translates this passive context into its own bounded steps and owns any tools, writes,
delegation, output, and completion validation. This document does not execute, call
tools, modify files, delegate work, load other skills transitively, grant authority, or
establish completion evidence. Any additional reference must be explicitly loaded by the
consuming operation.
