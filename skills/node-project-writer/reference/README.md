# Reference Index

This reference supplements the [production behavior change workflow](../SKILL.md). It
describes project context and evidence boundaries and routes each question to the page
that answers it; the operation entry point owns authorization, edits, commands, and
completion claims, and this index supplies context only.

## Project Context And Compatibility

Treat runtime, package manager, TypeScript processing, tests, quality checks, framework,
adapter, and artifact consumer as distinct project dimensions. Inspect the affected
package's effective configuration and relevant callers instead of inferring a complete
stack from a repository root, filename, manager, or framework label. Preserve established
public and behavioral contracts unless the requested change authorizes changing them.

Runtime examples are bounded illustrations, not a compatibility matrix: the cited Node.js
v26.13.0 documentation describes native TypeScript execution that strips erasable syntax
without type-checking and ignores `tsconfig.json`; Bun's documentation describes runtime
TypeScript/TSX transformation, which likewise does not make ordinary execution a type
check. Verify version-sensitive claims against the target project. A successful transform
or type check does not establish runtime behavior or compatibility in another environment.

## Outcome And Safety Boundaries

This owner covers production behavior changes and only regression coverage directly coupled
to those changes. Standalone tests-only work, dependency or environment changes, standalone
quality configuration, and package artifact or consumer validation have distinct owners.
Keep this general project outcome separate from repository utilities under `scripts/node/`.
Do not expand the operation into deployment, publication, or registry administration.

No workflow here selects or relies on Vite. That direct-workflow boundary is not a blanket
ban on transitive packages and does not prove that a framework's dependency graph is
Vite-free. Project-specific graph claims require exact versions and resolved dependency
evidence. Examples and operational context are descriptive, not universal security,
logging, observability, or reliability policy.

## Detailed Reference

The two routes answer different questions. Choose the page whose question matches the
change; the deciding evidence named in each route is what separates it from the other
page.

- **Which project facts matter to this change, and how to bound its validation?** Use
  [Change Design And Validation](change-design-and-validation.md) when the deciding
  evidence is the affected package, workspace, runtime, manager, compiler, runner,
  framework, adapter, or consumer, or the reach of validation. It covers effective
  project context, the production decision after conflicting clues, module configuration
  against the runtime loader, scoped regression tests, and validation evidence and
  limits. The full mixed-clue diagnosis is not repeated in that page: its canonical case
  is in the shared runtime reference
  (`node-project-reference -> reference/runtime-and-project-structure.md#reconcile-mixed-runtime-clues`),
  and the page keeps only the production decision about which clue decides the authorized
  change.
- **What must a change preserve for callers, and which caller-visible results, failures,
  timing, and side effects does it alter?** Use [Behavior And Caller
  Contracts](behavior-and-caller-contracts.md) when the deciding evidence is the called
  API's own contract: the returned result or state, the failure channel, the public
  runtime and type paths, timing and cancellation, and side effects. It covers the type
  surface against the runtime surface, cancellation as a request rather than rollback,
  consumer mismatch diagnosis, and version limits.

A route names a page and its question. Neither page is a step in a sequence, and a route
grants no operation, tool, edit, approval, or completion authority.
