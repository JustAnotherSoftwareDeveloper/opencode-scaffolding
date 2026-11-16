---
name: node-source-style-guide
description: "Use when contextual TypeScript source-style guidance is needed for a Node.js or Bun project."
selection:
  role: reference
  tags:
    actions: [reference, explain]
    inputs: [TypeScript source, project conventions]
    outputs: [contextual source-style guidance]
    topics: [imports, naming, comments, functions, values, async errors, types, modules, public APIs]
    environments: [Node.js projects, Bun projects]
    constraints: [passive, repository and API contracts take precedence]
  use_when:
    - the request asks how to interpret or apply TypeScript source conventions in a Node.js or Bun project
    - TypeScript authoring choices need contextual examples without selecting a universal style standard
  not_for:
    - changing production source, tests, lint or formatter configuration, or package artifacts
    - repository-specific deterministic utilities under scripts/node/
    - choosing a project-wide style policy or resolving a public API change without its contract
    - JavaScript-only source work, including JavaScript or mixed-language eligibility
    - JavaScript checking and diagnostics, such as allowJs and checkJs
    - JSDoc typing of .js files
class: documentation
---

# TypeScript Source-Style Reference

Use this passive reference for contextual TypeScript source conventions in Node.js and Bun projects. It offers examples and decision factors, not a universal house style, enforcement procedure, project decision, or source-edit authority.

TypeScript is the only source scope. Node.js and Bun runtime, module, loading, and emitted-JavaScript mechanics appear only where they explain how TypeScript source executes, emits, resolves, declares, or reaches a consumer, and TypeScript API documentation comments on exported declarations stay in scope. A JavaScript-only request is reported as out of scope. An authorized change stays on the TypeScript surface plus the manifests or configuration its authorization names, and JavaScript source edits are reported as out of scope rather than broadened into mixed-source authoring.

## Documentation Files

Read the page that answers the current question. A page's presence does not imply that its examples apply unchanged to another repository.

- [Contextual Source-Style Guidance](reference/source-style-guidance.md) — which evidence decides a TypeScript style choice, and where the detailed answer lives.
- [Imports, Names, And Comments](reference/imports-names-and-comments.md) — which import form makes a dependency clear, whether a name is local or caller-visible, and what a comment records.
- [Functions, Callbacks, Receivers, And State](reference/functions-callbacks-receivers-and-state.md) — whether a callback can be passed directly, whether a detached method keeps its receiver, and where instance state lives.
- [Values, Defaults, Objects, And Iteration](reference/values-defaults-objects-and-iteration.md) — whether `0`, `false`, and `""` count as absent, whether a copy isolates nested state, and how iteration differs by target.
- [Async And Error Boundaries](reference/async-and-error-boundaries.md) — whether a caller observes an async failure, which error channel an API uses, and how a caught `unknown` value narrows.
- [Types, Validation, And Generics](reference/types-validation-and-generics.md) — whether an assertion validates its input, whether `readonly` protects nested state, whether a generic preserves an input-output relationship, and which syntax Node can run without a transform.

## Boundaries

- Defer to applicable repository and package contracts, actual consumers, and tool configuration. Treat every example as an illustration: a style example does not override an API, runtime, or compatibility requirement, because a source-style preference is subordinate to the contract the code serves.
- Keep formatting, lint rules, source conventions, and public API design distinct. A formatter's output does not decide naming, module boundaries, or compatibility.
- Treat external guide examples as attributed examples scoped to their authors' contexts, not defaults for another project. Publisher pages are rolling, and no universal Node or Bun house style exists. A guide's example is not a compatibility promise for another package.
- This reference does not own implementation, tests, quality configuration, package distribution, compatibility approval, or validation. Nothing here selects or relies on Vite or forms an implicit pipeline.

## Passive Use

This is descriptive context only. It provides no workflow, tools, edits, policy decisions, or completion evidence. Ownership follows the surface, not the file: an authorized production source change belongs to `node-project-writer -> reference/change-design-and-validation.md`, rule enablement, target selection, and formatter or diagnostic mode belong to `node-quality-workflow -> reference/quality-scope-and-mutation.md`, and public API compatibility belongs to `node-project-reference -> reference/source-and-api-conventions.md`. These routes name ownership; they create no sequence, delegation, or approval.

## Docs

See the [Documentation Files](#documentation-files) above for the page that answers each question.
