# Consumer Resolution And Declarations

Use this reference when a consumer of a packed TypeScript package cannot import a subpath, when an export map must serve both `import` and `require` consumers, or when a typed consumer resolves a declaration that does not match the runtime target it loads. It owns the resolution-and-declaration question for the package-artifact workflow.

This page is the single canonical home of the four-layer packed-subpath diagnosis. Any other Node reference that needs this rule keeps only the cross-layer summary and points here rather than restating the layers.

The subject is the consumer-facing surface of a TypeScript package built for Node.js or Bun. Node.js and Bun runtime resolution and emitted-JavaScript mechanics appear only where they explain how TypeScript declarations and targets reach a consumer. JavaScript-only packages and mixed-language eligibility are out of scope, and a JavaScript-only request is reported as out of scope rather than answered with TypeScript guidance.

Diagnosis is not repair. Changing `exports`, emitted files, declarations, or source belongs to the owning operation and its authorization; a resolution finding does not imply publication, a release decision, or a compatibility promise.

## Start With The Cross-Layer Rule

A consumer asks for one exact specifier, under one runtime version, through one active condition, with one module-resolution mode. The package answers with metadata plus whatever files the archive actually contains. Those are separate facts, and the cross-layer rule is: isolate the layer that failed before assigning a cause, and do not transfer evidence from one layer to another.

The rule cuts in both directions. A runtime import that succeeds does not establish that TypeScript resolves declarations for the same subpath, and a declaration that type-checks does not prove that the runtime target exists in the archive or loads under the consumer runtime. One passing consumer also does not speak for another consumer with a different module format, condition, compiler version, or resolution mode.

For the delivered contract — package metadata, module-format evidence, build/pack/publish separation, actual-consumer testing scope, and registry limits — see [Artifact And Consumer Boundaries](artifact-and-consumer-boundaries.md). For which files a pack command would select and what an archive actually contained, see [Pack Preview And Archive Contents](pack-preview-and-archive-contents.md).

## Diagnose A Packed Subpath In Four Ordered Layers

Apply the layers in order because each later question presupposes an earlier answer, but treat the conclusions as independent. The four layers are one ordered diagnosis, not four separate files. An earlier pass does not clear a later layer, and a later failure does not prove that an earlier layer is sound.

The running example is `import { parse } from "widget/feature"` failing in a consumer that installed the package archive. “The package import failed” is not one diagnosis, and no single layer owns the failure.

1. **Tarball contents.** Establish whether the intended public target is in the archive that consumers receive. For npm, CLI v12 documents `npm pack --dry-run` as a prospective contents listing and `npm pack` as creation of a tarball ([npm pack](https://docs.npmjs.com/cli/v12/commands/npm-pack/)). A dry-run listing is not the archive, and a file present in the checkout or in `dist/` before packing is not evidence that package selection included it; `files`, ignore rules, and manager-specific exceptions decide that. A lifecycle hook such as `prepack` or `prepare` can also change the tree around `npm pack`, so inspect package scripts before treating a listing or a failed build as representative. A target that is missing from the archive is a packing fact. Editing the export map cannot fix it.
2. **The exact specifier against `exports`.** Once the file exists, compare the specifier the consumer wrote — exact key, pattern match, and subpath — with the package's export map and the condition that is active in that consumer. Node.js v26.13.0 documents that `exports` defines the public entry points when present, that it takes precedence over `main` for package-name resolution, and that subpaths it does not expose are not available through ordinary package-name resolution ([Node.js packages](https://nodejs.org/api/packages.html)). An unexposed subpath can fail with `ERR_PACKAGE_PATH_NOT_EXPORTED`. Conditional keys are matched in object key order, so the active condition depends on order as well as on the runtime. Do not test around the public contract by importing the private on-disk path of the installed package: that path is not the contract under examination, and its success says nothing about what consumers may use.
3. **The selected target under the consumer runtime.** If the subpath maps, confirm that the selected target exists in the archive and that its module format is compatible with the consumer's import form and runtime version. Node.js interprets `.mjs` as ESM and `.cjs` as CommonJS, and reads the nearest package `type` field for `.js` files. The same Node.js v26.13.0 page also documents syntax detection for otherwise ambiguous `.js` input as Stability 1.2 (Release candidate), so a `.js` target without an explicit marker deserves a version-checked reading rather than an assumption. The loader's error and the failing file identify the next question. Bun documents its own resolution conditions, including a `bun` condition that can point at TypeScript source ([Bun module resolution](https://bun.com/docs/runtime/module-resolution)); a Bun consumer can therefore select a different target than a Node consumer of the same package. Do not infer one runtime's resolution from the other's documentation.
4. **TypeScript declaration resolution.** A typed consumer runs a separate resolver inside the compiler, so check it as its own layer. TypeScript's Modules Reference documents that `node16` and `nodenext` resolution follow `exports` conditions, that the `bundler` mode also follows `exports` without requiring Node's runtime rules, and that extension substitution can locate a declaration after an export target is chosen ([TypeScript Modules Reference](https://www.typescriptlang.org/docs/handbook/modules/reference.html)). The legacy `node10` (also named `node`) resolution does not consult `exports`, so a subpath that only `exports` exposes can fail type resolution even while a modern Node runtime loads it — a different `moduleResolution` is a different consumer. Record the compiler version, the resolution mode, the active condition, and the declaration path that was actually resolved before concluding that a typed surface is absent. Declarations can resolve while the runtime target is missing in exactly the mirror image of a runtime pass with failed type resolution.

## Read The Export Map Branches And Conditions

`exports` is the public subpath contract; `main` remains the primary entry point for packages and resolution modes that do not use `exports`. When both are present, `exports` wins for package-name resolution, and a subpath that `exports` omits is not reachable by name, including when the file exists on disk. Object key order is part of the contract: conditions are tested in the order they appear, so a broad condition placed first can shadow a more specific one, and `types` must precede the runtime conditions in an object that TypeScript reads.

Describe `import` and `require` branches only where the package claims both. A package served only to ESM consumers needs one runtime branch and one declaration branch; adding a `require` branch asserts a CommonJS surface that must then be emitted, declared, and tested. Where the package claims both, each branch needs its own condition, its own emitted runtime file, and a declaration that describes that file's module format.

A single-branch map can be deliberate. This shape declares an ESM entry and a typed subpath, and it does not imply CommonJS support:

```json
{
  "type": "module",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js"
    },
    "./feature": {
      "types": "./dist/feature.d.ts",
      "import": "./dist/feature.js"
    }
  },
  "files": ["dist"]
}
```

Custom conditions extend the map only for consumers that request them. Node.js exposes its own condition set plus any `--conditions` values, and Bun documents its `bun` condition; TypeScript additionally matches `types` and any configured custom conditions. A condition key in a package manifest is therefore not evidence that every runtime, or every compiler configuration, activates it. A `null` target is a deliberate block, not a missing file, and a pattern such as `"./features/*"` shifts the diagnostic question to which file the pattern produced.

## Wire Declarations To The Branch That Serves Them

Declaration lookup is a metadata question before it is a file question. TypeScript's publishing guidance documents a top-level `types` field (with the historical alias `typings`) as the declaration entry point for consumers whose resolution does not pass through an `exports` type condition, and documents `typesVersions` for compiler-version-specific declaration folders ([TypeScript publishing](https://www.typescriptlang.org/docs/handbook/declaration-files/publishing.html)). Under `exports`-based resolution, express the declaration target as a `types` condition instead, and place it before the runtime condition in each object.

The supported forms have different reach:

- A top-level `types` or `typings` field names one declaration entry for the package root. It cannot describe per-subpath or per-branch declarations.
- A conditional `types` inside `exports` is matched by the compiler's condition matching and can point each branch at its own declaration file. It must come first in the object; a `default` or `import` key that precedes it can win the match.
- A versioned condition such as `"types@>=5.2"` is matched by the same version-selection rules TypeScript implements for `typesVersions`, so older and newer compilers can receive different declarations from one map.
- `typesVersions` maps compiler-version ranges to declaration directories. It is not a guarantee once `exports` is involved: the compiler still refuses unlisted subpaths, so a versioned declaration folder cannot make an unexported specifier resolve. A `paths` mapping, where configured, overrides `main`, `types`, `exports`, and `typesVersions`.

Declaration file names are part of the mechanics, not decoration. After choosing an export target, TypeScript applies extension substitution: an `.mjs` target looks for a `.d.mts` declaration, a `.cjs` target for a `.d.cts`, and a `.js` target for a `.d.ts`, with the surrounding package scope supplying the format for the `.js` case. The declaration's own extension and nearest package `type` also fix the module format in which the declaration is interpreted, so a single `.d.ts` cannot truthfully describe both a `"type": "module"` ESM target and a CommonJS target when their export surfaces differ. Check the exact names and substitutions against the Modules Reference for the consumer's compiler version; the names are documented behavior, not a naming convention this page may invent.

Emitting declarations is a compiler capability, and wiring them is a package-metadata decision. TypeScript documents `declaration` and `emitDeclarationOnly` as declaration-emit options ([TSConfig reference](https://www.typescriptlang.org/tsconfig/)); `emitDeclarationOnly` writes declarations without JavaScript. Neither option proves that the declarations were packed, that `exports` or `types` points at them, or that a consumer resolves them. A bundler's declaration flag is a publisher-specific path with the same gap.

Not every package needs dual formats or typed support. A package consumed only by ESM code in one workspace does not need a `require` branch; an internal package whose consumers do not compile against it does not need published declarations. Adding either expands the public surface and creates another branch and declaration to emit, pack, and verify. The absence of a branch or of declarations is a contract statement, not automatically a defect, and the consumer's actual requirement decides.

### Distinguish Bundled Declarations From Installed Declaration Packages

A package can bundle its own declarations by emitting `.d.ts` files and pointing `types` or a `types` condition at them. A consumer can instead resolve declarations from a separately installed declaration-only package, conventionally published under the `@types` scope by DefinitelyTyped; the name maps the underlying package (`foo` becomes `@types/foo`, and a scoped `@scope/name` becomes `@types/scope__name`). A declaration-only package contributes compile-time types rather than runtime code, a distinction the publisher documentation describes rather than an observation this page can make. Its dependency role follows the field its author chose and the tool that reads it, so a declaration-only package can be a production install or a development install, and the field name alone does not prove runtime execution or non-execution.

Ambient and imported declaration lookup are also distinct. The `types` compiler option filters which packages contribute global scope during compilation, and `types: []` does not disable declaration resolution for an explicitly imported package. `typeRoots` is a different option: since TypeScript 5.1 it participates as a module-resolution fallback when the normal lookup fails, and an explicit `typeRoots` disables the upward walk through parent `node_modules/@types` folders, which can surface `TS2688: Cannot find type definition file` ([TypeScript 5.1 release notes](https://devblogs.microsoft.com/typescript/announcing-typescript-5-1/)). TypeScript 6.0 changes the `types` default to `[]`, replacing the earlier default that included everything under `node_modules/@types`; `"types": ["*"]` restores the 5.9 behavior ([TypeScript 6.0](https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/)). Version bounds matter here because each of these statements names the release that introduced it.

When a package's own emitted declarations expose types from another package, TypeScript's publishing guidance says to put that declaration package in `dependencies`, because consumers' compilation needs it too; the guidance concerns declaration dependencies whose types leak into the published signatures, not a rule that every package must depend on its own `@types`. `@types` packages are published with a matching major/minor version and an independently incremented patch, and updates commonly lag the library. That alignment is a publishing convention and not a compatibility guarantee: a matching major/minor does not prove type or API compatibility.

## Verify The Installed Archive

Consumer evidence must come from the artifact a consumer receives, exercised on the route it claims. The minimal chain has four steps:

1. Inspect the archive: read the actual tarball's file list and package metadata, not a dry-run listing and not the working tree.
2. Install that archive into a separate consumer project, rather than linking the source tree, the workspace package, or a local directory.
3. Exercise only the runtime forms the request names — the exact specifier, subpath, condition, module format, and runtime version.
4. Run a separate TypeScript consumer check when declarations are in the contract, recording the compiler version and the `moduleResolution` mode alongside the resolved declaration path.

The second step is where linked and packed consumption diverge. A workspace symlink or `file:` link resolves through the file system to the source package, so it can expose files the archive omits, skip package selection entirely, and follow the source package's own development metadata. A source-tree test therefore does not establish packed contents, and a linked import cannot stand in for installing the archive.

The archive is identified by its bytes, not by its extracted tree. Registry `dist.integrity` and lockfile `integrity` or `resolution.integrity` values record digest metadata for the tarball; extraction, symlinks, and build transforms change file bytes, so comparing an installed or linked tree against a tarball digest compares different layers and establishes nothing about the archive. A matching digest shows that the artifact matches the recorded value; it does not show that the expected party published it, and provenance describes a build context rather than safety. Treat these as layer-correct evidence boundaries, not as a verification procedure.

The pack and install mechanics are manager- and version-scoped. npm CLI v12 documents `npm pack --dry-run` as prospective and `npm pack` as archive creation, and those statements are npm's. `bun pm pack` is Bun's own implementation; Bun's page describes npm-pack-like rules, while Bun's repository implements its own include and exclude walk, so exact npm parity is not established ([Bun pm](https://bun.com/docs/pm/cli/pm)). A local archive install also does not test registry publication, access controls, or registry attestations.

## Worked Examples

These are illustrative combinations of the documented mechanics, not executed package tests.

**An ESM pass with a failed CommonJS declaration.** A package exposes `./feature` with an `import` branch that has both a runtime target and a `types` target, and a `require` branch that has only a runtime target. An ESM consumer imports the subpath: the runtime loads and its type check passes. A typed CommonJS consumer of the same archive loads the module at runtime but fails its type check because the `require` branch gives that consumer no declaration for the subpath it resolved. The reported code depends on the resolution outcome: a JavaScript file found without a declaration yields `TS7016`, while a resolution that finds nothing yields `TS2307`. Either way the ESM result does not transfer, because a runtime pass in one module format does not establish declaration resolution in the other.

**A dual-format map with per-branch declarations.** This map claims both formats, and each branch carries its own condition, emitted file, and declaration:

```json
{
  "name": "widget",
  "type": "module",
  "exports": {
    "./feature": {
      "import": {
        "types": "./dist/feature.d.mts",
        "default": "./dist/feature.mjs"
      },
      "require": {
        "types": "./dist/feature.d.cts",
        "default": "./dist/feature.cjs"
      }
    }
  },
  "files": ["dist"]
}
```

The `.d.mts` and `.d.cts` names are the extension-substitution results for `.mjs` and `.cjs` targets described by the TypeScript Modules Reference, and the nested `types` condition is first in each object. The names follow the documented substitution rules; confirm them against the reference for the compiler version in use rather than copying them as a style choice.

**A runtime load with a missing type for the same subpath.** A consumer imports a subpath that resolves to an emitted JavaScript file, the module loads and runs, and `tsc --noEmit` reports `TS7016: Could not find a declaration file for module 'widget/feature'. '/…/node_modules/widget/dist/feature.mjs' implicitly has an 'any' type.` Here resolution succeeded and produced a JavaScript file; the declaration layer failed on its own. The runtime result is not evidence about the type surface, and the type result does not mean the file is missing from the archive.

**Declaration resolution per branch.** For the dual-format map above, a compiler running in `nodenext` resolution against an `import` consumer resolves the `types` condition to `dist/feature.d.mts`, while a `require` consumer resolves to `dist/feature.d.cts`; under `node10`, the same map's subpath resolves only through the legacy lookup, which does not consult `exports`. The evidence to record is the resolved declaration path and the mode that produced it, not merely the presence of a `types` key in the manifest.

## Read The Diagnostic Before Assigning A Cause

Each layer produces a different observable, and the observable names the layer to investigate next:

- `ERR_PACKAGE_PATH_NOT_EXPORTED` belongs to the runtime export map, not to a missing declaration. Verify the exact subpath key or pattern and the active condition in the packed manifest first; adding a `.d.ts` file cannot resolve a runtime export-map rejection, and a declaration fix aimed at this error is aimed at the wrong layer.
- A loader or module-format error — a syntax error on an ESM-only construct, or a message that the format is incompatible with the import form — belongs to the selected target and the consumer runtime. Confirm the target's extension and nearest `type`, then compare against the consumer's runtime version; this is not an `exports` diagnosis and not a type diagnosis.
- `TS2307: Cannot find module 'X' or its corresponding type declarations.` is the type resolver reporting that nothing resolved for the active resolution mode. Check the mode, whether that mode consults `exports`, the subpath, and the condition before attributing it to a missing file on disk.
- `TS7016: Could not find a declaration file for module '{0}'. '{1}' implicitly has an 'any' type.` is the different case in which the specifier resolved to a JavaScript file with no declaration. In the pinned TypeScript 5.9.3 compiler it is emitted through the `errorOrSuggestion` path: it is an error when `noImplicitAny` is enabled and the module lookup carries a module-not-found condition, and otherwise it is still produced, but as a suggestion diagnostic that `tsc` does not print and that a language service can surface. The module is `any` in both cases, so disabled `noImplicitAny` weakens the diagnostic's severity and display surface, not the untyped import. The emitter condition is a resolution to a non-TypeScript, non-JSON file without a declaration. TypeScript 6.0's `strict` default changes which unconfigured projects see this as an error.
- A declaration that resolves but describes the wrong module format is a fourth case: the path exists, and the checker rejects how the declaration can be consumed from that module context. Inspect the resolved declaration's extension and package scope before concluding that declarations are absent.

The error-versus-suggestion condition for `TS7016` is stated canonically, with the `TS2307` neighbor and the version bounds, in `node-quality-workflow -> reference/quality-scope-and-mutation.md`. Read that page for the diagnostics-versus-writes framing; do not extend the pinned condition to every resolver, module mode, or TypeScript 7.x.

## Bun Declaration Generation Is An Unresolved Publisher Conflict

Bun's declaration-generation documentation is internally inconsistent, and the conflict stays visible. The Bundler page's overview says `bun build` does not generate declarations and directs users to `tsc`, while the same page's later `dts` section documents declaration output; the `BuildConfig.dts` reference and the Libraries page also document declaration generation and its output contract ([Bun Bundler](https://bun.com/docs/bundler), [`BuildConfig.dts`](https://bun.com/reference/globals/bun/BuildConfig/dts), [Bun Libraries](https://bun.com/docs/compiler/libraries)). This is a publisher documentation disagreement, not evidence that the capability is absent or that it is universally available.

The bounded observations do not collapse the conflict. On installed Bun 1.3.14, `bun build ./src/index.ts --outdir ./dist --dts` exited 0 and wrote only `dist/index.js`, with no declaration files, and `bun build --help` did not list `--dts`. Newer Bun repository tests at commit `8d5672c` assert `.js`, `.d.ts`, and `.aot.ts` artifacts and treat type errors as build failures, and a Bun canary release `1.4.4-canary.1` documents `--dts`. The reference also documents that declaration output needs `outdir` for CLI disk output and is incompatible with `compile` mode. These statements support a newer, version-specific capability. No primary Bun statement identifies the first stable release that shipped it, so that release remains unknown.

The practical reading is bounded in both directions. Do not treat the 1.3.14 observation as a universal “Bun cannot generate declarations” rule, and do not project canary or source evidence back onto 1.3.14 or onto every stable release. Verify the selected Bun release's actual output before relying on `--dts`, and verify packed declaration presence and consumer resolution separately. Bun's `.aot.ts` output and `aot` export condition belong to Bun's own compilation path and are not claims for another runtime or for ordinary Node consumers.

## Keep Limits And Ownership Explicit

Declaration lookup depends on compiler version, resolution mode, and compiler options; a result under one combination does not generalize. The exact declaration file names, substitution behavior, and diagnostic message text are documented behavior that must be checked against the TypeScript Modules Reference and the pinned compiler source for the version in use. npm and Bun documentation is version-scoped or rolling, and no reader study or measured compatibility matrix supports claims that this page's routing or examples improve outcomes.

Consumer validation of the packaged output belongs to this operation. Source-level style and API design route to `node-project-writer` and the style guide, and standalone quality diagnostics route to `node-quality-workflow`; dependency and installation changes route to `node-project-dependencies`. A proposed metadata, output, declaration, or source change needs the relevant owner and authorization, and this page implies no publication or deployment.

Cross-links for the surrounding questions:

- Delivered contract, build/pack/publish separation, and consumer evidence limits: [Artifact And Consumer Boundaries](artifact-and-consumer-boundaries.md).
- Prospective file selection and archive contents: [Pack Preview And Archive Contents](pack-preview-and-archive-contents.md).
- Shared public-surface, module-context, and compatibility conventions: `node-project-reference -> reference/source-and-api-conventions.md`.
- Declaration and type-surface design guidance: `node-source-style-guide -> reference/types-validation-and-generics.md`.
- Canonical `TS7016`/`TS2307` diagnostic wording and severity conditions: `node-quality-workflow -> reference/quality-scope-and-mutation.md`.
