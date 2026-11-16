# Source And API Conventions

This page answers why an import of a packed subpath fails and what a declaration, a public name, or a runtime module format changes for a consumer. It owns the shared cross-layer rule and the public-compatibility boundary for TypeScript source and declarations in Node.js or Bun projects; a JavaScript-only request is out of scope. Everyday source choices — import form, names, comment placement, file boundaries, and public-surface preferences — belong to the style workspace: start from `node-source-style-guide -> reference/source-style-guidance.md`.

## Keep The Cross-Layer Rule For A Packed Subpath

A consumer asks for one exact specifier under one runtime version, one active condition, and one module-resolution mode; the package answers with metadata plus the files its archive actually contains. Those are separate facts, and the cross-layer rule is: isolate the layer that failed before assigning a cause, and do not carry evidence from one layer into another. A runtime import that succeeds does not establish that TypeScript resolves a declaration for the same subpath, and a declaration that type-checks does not establish that the runtime target is in the archive or that the consumer's runtime loads it. One passing consumer also says nothing about a consumer with a different module format, condition, compiler version, or resolution mode.

The four questions behind that rule — what the tarball contains, how the exact specifier matches `exports`, which target the consumer runtime selects, and how TypeScript resolves the declaration — form one ordered diagnosis with one canonical home: `node-package-distribution -> reference/consumer-resolution-and-declarations.md#diagnose-a-packed-subpath-in-four-ordered-layers`. This page keeps the rule and points there for the layer order, the export-map branches, the install-and-check chain, and the declaration mechanics; it does not restate them.

## Map Each Failure To Its Layer

The observable names the layer to inspect next, and "the package import failed" is not one diagnosis:

- `ERR_PACKAGE_PATH_NOT_EXPORTED` points first to the runtime export map. Node.js v26.13.0 documents that `exports` defines the public entry points and that a subpath it omits is not reachable through package-name resolution ([Node.js packages](https://nodejs.org/api/packages.html)); a declaration cannot clear that rejection.
- A loader or module-format error points to the selected target — its presence in the archive, its extension, and the nearest package `type` under the consumer's runtime version — not to `exports` and not to declaration resolution.
- An unresolved import, or an import that resolves to `any` for lack of a declaration, points to TypeScript declaration resolution under the consumer's compiler version and `moduleResolution` mode ([TypeScript Modules Reference](https://www.typescriptlang.org/docs/handbook/modules/reference.html)).

Attributing the message to a single cause skips the layer that produced it, and a fix aimed at the wrong layer leaves the failure intact.

## Public Compatibility Boundaries

Error propagation belongs to each API's documented contract: a call may throw synchronously, reject a promise, invoke an error callback, or emit an `error` event, and handling one channel does not observe another. For Node core errors, Node documents `code` as more stable across minor versions than `message`; that statement covers Node's own errors and does not extend to a third-party package's error shape.

An exported name, a package subpath, a declaration file, and the runtime module format are one consumer-facing surface. Removing a name or subpath that a consumer already uses breaks that consumer, narrowing visibility reduces accidental coupling, and a module-format change can break a consumer whose declaration still compiles.

Declarations describe a static interface. Their layout depends on the package module form and the consumer's resolution settings, and the shape they present decides what a caller can compile: structural compatibility, the order of overload signatures, optional and rest parameters, and function-parameter rules all affect assignability or inference, so reordering overloads can change which signature a caller resolves ([TypeScript Handbook: More on Functions](https://www.typescriptlang.org/docs/handbook/2/functions.html)). Compiler version and options bind each of those results.

These are compatibility considerations, not a semantic-versioning policy or a claim that every change is breaking. A compiling declaration does not prove runtime behavior, and a runtime change made without its declaration leaves typed consumers compiling against a shape the code no longer implements.

## Separate A Declared Contract From Runtime Validation

A JSDoc or TSDoc type expression records an intent for readers and tools; it does not validate input at runtime. For example, document the caller-facing contract and keep the implementation note internal:

```ts
/** Parse a configuration string; throws SyntaxError when its JSON is invalid. */
export function parseConfig(text: string): Config {
  // Keep the parser choice internal; callers depend on the contract above.
  return JSON.parse(text) as Config;
}
```

This illustration is truthful only if the implementation really throws that error and the cast is justified by validation elsewhere; `as Config` does not validate input. A project may instead return a result type or validate with a runtime schema. Choose from the existing API contract and the actual validation mechanism rather than treating the snippet as a preferred parser design.

## Limits And Evidence

Node.js v26.13.0 documents export-map behavior and unexported-subpath failures; another Node release or another runtime documents its own conditions. TypeScript declaration lookup depends on the compiler version and the resolution settings in effect, so a result describes that combination rather than TypeScript generally. npm's pack documentation describes npm's own CLI and file selection, not another manager's package contents. No package, compiler, or runtime was tested for this page, and its examples document stated behavior rather than project evidence.

## Ownership And Cross-Links

This page owns shared interpretation only. It changes no source, declaration, or package metadata, and it grants no edit, release, or publication authority.

- Source-style decisions belong to the style workspace: `node-source-style-guide -> reference/source-style-guidance.md`.
- The four-layer diagnosis, export-map branches, declaration wiring, and artifact validation belong to `node-package-distribution -> reference/consumer-resolution-and-declarations.md`; a requested fix goes to the operation that owns the changed surface.
- Runtime execution, module kind, and resolution evidence belong to [Runtime And Project Structure](runtime-and-project-structure.md).
