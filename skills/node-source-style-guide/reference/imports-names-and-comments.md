# Imports, Names, And Comments

This page holds three connected decisions at a module's edge: which import form makes a dependency readable, which names are local and which are caller-visible, and which comments record a constraint and which document a caller contract. It then walks one conflict where formatter output, lint configuration, neighboring code, a publisher guide, and a caller contract all bear on the same change.

Keep two kinds of claim apart throughout. Some choices have an observable language, type, or emit consequence; others are conventions whose rationale is reader comprehension, consistency, tooling, or churn avoidance. No universal import or naming rule exists, and a publisher's convention applies to that publisher's codebase unless the target project adopts it.

## Choose An Import Form For The Surface

Google's TypeScript style guide documents both forms as its own considerations: it prefers named imports for symbols that are common or clear, and namespace imports when a module supplies many symbols or a common name needs disambiguation ([Google TypeScript style guide](https://google.github.io/styleguide/tsguide.html)). The guide states conventions for code written in its own environment and warns that those constraints may not transfer, so read the preference as an attributed example of one consideration, not as a default for another repository.

```ts
import { parseConfig } from "./config.js";
import * as dateTools from "./date-tools.js";
```

Both forms resolve the same module and bind the same exports. A named import binds individual exports to local names; a namespace import binds one local name to the module object. The difference is how the dependency and symbol origin read at the call site, and how easily a local name collides. That is a reader and navigation effect, not a change to the module's public contract, load behavior, or export shape.

Decide with the target module's convention:

- Check the package format and the resolver that actually runs the code before choosing a specifier form. Relative specifier rules, extension requirements, and module kind are mechanical constraints owned by `node-project-reference -> reference/runtime-and-project-structure.md#module-kind-and-resolution`; this page does not restate them.
- Treat a supported named export or subpath as a contract. A named import does not make an internal helper public, and a namespace import is not a substitute for a package boundary.
- Prefer the form that the module's own maintained files use when both forms are mechanically valid. A neighboring file is evidence of local practice, not proof that the current file must match.

## Mark Type-Only Imports And Exports

A name used only in a type position can be imported or re-exported with `import type` and `export type`. The syntax is erased: it leaves no runtime artifact, so the declaration-side import graph and the runtime import graph can differ by design.

```ts
import type { RetryOptions } from "./options.js";

export type { RetryOptions };
```

TypeScript 3.8 introduced the syntax and states that `import type` "always gets fully erased, so there's no remnant of it at runtime", with `export type` erased as well ([TypeScript 3.8 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-8.html)). The Modules Reference generalizes the guarantee: default emit elides imports used only in type positions, and `import type`, `export type { ... }`, and `type`-prefixed specifiers are guaranteed to be elided ([TypeScript Modules Reference](https://www.typescriptlang.org/docs/handbook/modules/reference.html)).

Erasure also restricts use. A value imported with `import type` can only appear in non-emitting positions; using it as a value is a compiler error, reported as "cannot be used as a value because it was imported using `import type`".

### Node's Native Path Requires The Keyword

When Node executes TypeScript directly, it strips types and does not check them, and its v26 documentation requires the explicit `type` keyword: "Without the `type` keyword, Node.js will treat the import as a value import, which will result in a runtime error" ([Node.js Modules: TypeScript](https://nodejs.org/docs/latest-v26.x/api/typescript.html)). The type has no runtime binding, so a value import of it fails when the module loads rather than when the checker runs. The same page names `verbatimModuleSyntax` as the compiler setting that matches this behavior.

### Emit Rules Depend On Compiler Options

Default emit is usage-driven: the compiler decides from declaration information which imports and exports survive. `verbatimModuleSyntax` (TypeScript 5.0) replaces that with a syntactic rule: "any imports or exports without a `type` modifier are left around. Anything that uses the `type` modifier is dropped entirely" ([TSConfig `verbatimModuleSyntax`](https://www.typescriptlang.org/tsconfig/verbatimModuleSyntax.html)). Documented rewrites include `import { b, type c, type d }` becoming `import { b }`, and `import { type xyz }` becoming `import {} from "xyz"` ([TypeScript 5.0 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-0.html)).

The option also blocks module rewriting. ECMAScript `import`/`export` are not rewritten to `require` when the file's settings or extension imply another module system; the compiler reports an error instead, and CommonJS output must use `import foo = require("foo")` or `export =`.

Two adjacent options complete the picture. `isolatedModules` warns about code that single-file transpilation cannot interpret correctly; it does not change checking or emit, it was released in TypeScript 1.5, and its default is `true` when `verbatimModuleSyntax` is enabled and `false` otherwise, so that coupling is an interaction rather than a second opt-in ([TSConfig `isolatedModules`](https://www.typescriptlang.org/tsconfig/isolatedModules.html)). `importsNotUsedAsValues` was the earlier control, introduced with `import type` in 3.8. It was deprecated in TypeScript 5.0 in favor of `verbatimModuleSyntax`; the 5.5 release notes say the 5.0 deprecations no longer have any effect and would be an error to specify in 6.0; and in 6.0 the option is removed, with the compiler reporting `TS5102` "Option 'importsNotUsedAsValues' has been removed" ([TSConfig `importsNotUsedAsValues`](https://www.typescriptlang.org/tsconfig/importsNotUsedAsValues.html)).

The practical consequence is mechanical, not stylistic: under `verbatimModuleSyntax` a missing `type` modifier makes the import a runtime import, so a type that has no runtime binding becomes an emit or load problem rather than being silently dropped at compile time.

## Keep Local Names And Exported Names Separate

A local binding name exists for the reader of the file. `retryPolicy` says what the value governs; `cfg` makes the reader recover that meaning from the initializer and the later uses.

```ts
// Local binding: no caller observes this name.
const retryPolicy = options.retryPolicy ?? defaultRetryPolicy;

// Placeholder: the reader has to recover the meaning from the initializer.
const cfg = options.retryPolicy ?? defaultRetryPolicy;
```

Renaming a local binding, or importing an export under a clearer local alias, is a comprehension choice with no runtime or type consequence for anyone outside the file. Google's guide asks for descriptive names and applies casing by identifier category; the TypeScript contributor guidelines add repository rules such as no `I` prefix on interfaces and no leading underscore on private properties ([TypeScript coding guidelines](https://github.com/microsoft/TypeScript/wiki/Coding-guidelines)). Both are attributed publisher policies. Casing is not maintained by the compiler, and no language rule requires either convention.

The following names are different because callers observe them:

- An exported symbol. Renaming or removing it changes a caller-visible contract; typed consumers that import the old name fail to compile, and Google's guide shows the missing-member case as `error TS2614: Module '"./foo"' has no exported member 'fizz'` ([Google TypeScript style guide](https://google.github.io/styleguide/tsguide.html)).
- A serialized field. Renaming it changes stored or transmitted data, and existing payloads keep the old key.
- A command option or an environment variable. Renaming it changes an external interface that scripts, deployment configuration, and documented invocations rely on.

Treat those changes as API decisions, not style cleanups. The rationale for a local rename is reader comprehension; renaming an exported or otherwise observable name changes what someone else can depend on.

## Write Comments For What The Code Cannot Say

An implementation comment earns its place by recording intent, an invariant, a constraint, or a tradeoff that the code cannot state. A comment that paraphrases the next line does not.

```ts
// Keep the final newline: the downstream line-oriented reader treats it as a record.
const output = `${serialized}\n`;
```

Compared with `// Append a newline.`, the first comment records why the newline must stay, which is not visible in the expression; the second repeats what the expression already shows. Keep a comment that records a compatibility constraint even when the code looks self-evident, and delete a comment that only restates the operation.

A documentation comment on an exported declaration is a different artifact: a caller-facing contract. Google's guide separates `/** JSDoc */` written for code users from ordinary comments for implementation notes, and notes that tools can consume the documentation form ([Google TypeScript style guide](https://google.github.io/styleguide/tsguide.html)).

```ts
/**
 * Load retry settings from a configuration file.
 * Missing fields take documented defaults; an invalid file throws.
 */
export function loadRetryOptions(path: string): RetryOptions {
  return parseRetryOptions(readFileSync(path, "utf8"));
}
```

Document what a caller must know: rejected input, thrown errors, defaults, and side effects that the signature does not convey. Do not restate the parameter list.

A documentation comment states an intent; it does not enforce one. The compiler does not check prose, and a JSDoc or TSDoc type expression does not validate a runtime value; the declaration and the runtime behavior must agree independently. Comment wording and placement have no effect on checking, emit, or execution, so the rationale for either comment form is reader comprehension and, for documentation comments, the tooling that renders them. Type-level guarantees and runtime validation belong to `types-validation-and-generics.md`, which owns that question.

## Walk One Alias-Versus-Interface Conflict

Suppose a package exports an object type alias:

```ts
export type RetryOptions = {
  attempts: number;
  backoffMs: number;
};
```

The interface form declares the same members and adds a merge point:

```ts
export interface RetryOptions {
  attempts: number;
  backoffMs: number;
}
```

A formatter reprints the file. A reviewer proposes replacing the exported alias with an `interface`, citing two neighboring modules that use interfaces and Google's preference for interfaces on object shapes. The package's typed consumers import `RetryOptions`. Work each source for what it can establish rather than counting votes.

- **Formatter output establishes layout.** Prettier documents parsing and reprinting to produce consistent formatting ([Prettier](https://prettier.io/docs/en/)). It can change brace and line placement; it does not choose between `type` and `interface`. Its rewrite is not evidence for the change, and a formatter that left the file alone would not be evidence against it.
- **The effective lint configuration establishes only the enabled rule, its option, and its target set.** typescript-eslint documents `consistent-type-definitions` as a configurable consistency rule that can require either form, records the semantic differences, and notes cases where conversion is unsuitable ([`consistent-type-definitions`](https://typescript-eslint.io/rules/consistent-type-definitions/)). The page does not show that this package enables the rule, which option it selects, or which files it covers. Read the actual configuration and the invocation's target set; a documented rule is not an adopted rule, and the guidance for that read belongs to `node-quality-workflow -> reference/quality-scope-and-mutation.md`.
- **Neighboring modules establish local practice.** Files that export interfaces are evidence of what this repository currently does. They are not proof that the pattern was deliberate, current, or correct, and they do not override a caller contract.
- **Google's guide establishes a scoped preference.** It prefers `interface` for object shapes in code written for its own environment. Its applicability warning limits that preference to that context, so it is one attributed consideration among the others here, not a deciding rule.
- **TypeScript semantics establish what a conversion changes.** Interfaces with the same name merge when they are compatible and are rejected when they are not; a type alias is a single named type and provides no such merge point. An alias can also express a union, an intersection, or another form an interface cannot declare directly ([TypeScript Handbook: Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)). A conversion preserves behavior only when neither merging nor a non-object form is involved.
- **The package contract and its consumers decide.** Typed consumers resolve the declaration shape, so the exported form is part of the package's API surface. Whether any consumer augments the type, and whether the export must stay a union, decides more than any of the sources above.

Apply the walk in that order:

1. If the export is a discriminated union or another non-object form, conversion to an `interface` is unavailable. Record it as unavailable, not as a style preference:

```ts
export type RetryPolicy =
  | { kind: "fixed"; delayMs: number }
  | { kind: "exponential"; baseMs: number; factor: number };
```

2. If the project's effective configuration enables the rule with the `interface` option for these files, that configuration is the local requirement and the conversion satisfies it.
3. If the export is a plain object shape and a consumer augments the exported type, the conversion changes observable type behavior. The alias offered no merge target; after conversion the consumer's augmentation merges, and a merge with conflicting members is rejected rather than silently ignored. Check the exact rules and diagnostics against the object-types documentation for the compiler version the package supports before asserting the outcome.
4. If none of those applies, the remaining choice belongs to the package owner. Name that owner in the review rather than letting a formatter, a rule page, or a neighboring file settle it.

## What Fails, And Where

- Node's native path treats a type-only import written without `type` as a value import and fails when the module loads, because the type has no runtime binding.
- A compatible object type alias converted to an `interface` gives consumers a merge target; a discriminated union has no equivalent interface form, so that conversion is not available there.
- A consumer whose augmentation conflicts with the converted declaration fails to compile after the conversion; verify the diagnostic on the supported compiler rather than predicting a code from this page.
- Using a name imported with `import type` as a value is a compiler error, not a runtime surprise.
- Specifying `importsNotUsedAsValues` in TypeScript 6.0 produces `TS5102`, because the option has been removed.
- A green formatter or lint run reports only what that tool did to the files it selected; it does not establish declaration compatibility, runtime loading, or consumer resolution.

## Limits And Ownership

- `import type` and `export type` date from TypeScript 3.8; `verbatimModuleSyntax` from 5.0; `isolatedModules` from 1.5 with its default coupled to `verbatimModuleSyntax`; `importsNotUsedAsValues` deprecated in 5.0 and removed in 6.0.
- Rule documentation establishes an available rule, not a project's enablement, option, or target set. Read the effective configuration and the invocation.
- Interface merging behavior is recorded from TypeScript's object-types documentation; the page is rolling, so check the current text for the compiler version in use.
- All examples here are non-normative illustrations. They show a decision shape, not a required house style.
- This page provides style guidance only. A change to an exported name or declaration goes to the production owner (`node-project-writer -> reference/change-design-and-validation.md`) or, when the consumer contract or package artifact is at stake, to `node-package-distribution -> reference/consumer-resolution-and-declarations.md`, together with the contract that change affects.
- Formatter and lint configuration belongs to `node-quality-workflow -> reference/quality-scope-and-mutation.md`.
- Module format, relative specifier requirements, and loader behavior belong to `node-project-reference -> reference/runtime-and-project-structure.md`; the public source and API surface is covered by `node-project-reference -> reference/source-and-api-conventions.md`.
- The method for weighing these sources, and the routing across the style pages, stays with the hub, [Contextual Source-Style Guidance](source-style-guidance.md).
