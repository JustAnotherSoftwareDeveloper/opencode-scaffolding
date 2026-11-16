# Reference Map

This workspace is passive TypeScript source-style context for Node.js and Bun projects, indexed over one method hub and five answer pages. It routes a source question to the page that answers it, and it decides no style question itself.

## Question Routes

Each route names the page that owns the question and the clue that separates that page from its neighbors.

- **Which evidence decides this style choice?** [Contextual Source-Style Guidance](source-style-guidance.md) — the method page: it separates formatter output, configured diagnostics, established source patterns, and the behavior promised to callers, and it labels each statement as a hazard with an observable consequence or a convention bound only to the publisher that states it.
- **Which import form, and which naming surface?** [Imports, Names, And Comments](imports-names-and-comments.md#choose-an-import-form-for-the-surface) — named versus namespace imports, type-only imports and exports, local versus caller-visible names, and implementation comments versus caller contracts, with one alias-versus-interface conflict walked through each source of evidence.
- **Does this callback keep its receiver, or should this value initialize as a class field?** [Functions, Callbacks, Receivers, And State](functions-callbacks-receivers-and-state.md#read-the-receiver-from-the-call-site-not-the-definition) — `this` read from the call site, the argument list a callback actually receives, field versus constructor-local state, and `private` versus `#` visibility.
- **Do `0`, `false`, or `""` count as absent, and does this copy isolate nested state?** [Values, Defaults, Objects, And Iteration](values-defaults-objects-and-iteration.md#treat-falsy-and-absent-as-different-questions) — the falsy set kept apart from absence and defaulting, a one-level spread copy separated from the nested values it still shares, and value iteration contrasted with key iteration.
- **Would a caller observe this async failure?** [Async And Error Boundaries](async-and-error-boundaries.md#make-failure-reach-the-caller) — whether the failure reaches the caller's return path, which channel the API's own contract names, how a caught `unknown` narrows, and why cancellation is a request rather than a rollback.
- **Does this assertion validate its input?** [Types, Validation, And Generics](types-validation-and-generics.md#read-an-annotation-differently-from-an-assertion) — a checked annotation separated from an erased assertion, `readonly` and generic preservation bounded to what the compiler proves, and the syntax Node executes without a transform.

## Applicability

Use only the portions relevant to the source and project at hand. The pages cover TypeScript source, including documentation comments on exported declarations; runtime, module, loading, and emitted-JavaScript detail appears only where it explains how that source executes, emits, resolves, or reaches a consumer. JavaScript-only source work is out of scope.

The named guides document their publishers' conventions; they do not establish a universal standard, because each guide is scoped to its own codebase or documentation system. Publisher pages are rolling and can change, so an attributed example describes the page as read rather than a standing rule.

## Owner Routes

A question that leaves style context belongs to an owner, and naming that owner starts no work:

- An authorized production source change: `node-project-writer -> reference/change-design-and-validation.md`.
- Rule enablement, target selection, and formatter or diagnostic mode: `node-quality-workflow -> reference/quality-scope-and-mutation.md`.
- Public source and API compatibility: `node-project-reference -> reference/source-and-api-conventions.md`.
- Package entry points and declaration consumption: `node-package-distribution -> reference/consumer-resolution-and-declarations.md`.

## Index Boundary

This map is an index only. It routes rather than answers, states no style rule, and grants no tool, edit, approval, delegation, sequence, or completion authority.
