# Artifact And Consumer Boundaries

Use this reference for package metadata, emitted files, packed artifacts, and consumer checks. The operation entry point owns authorization, commands, writes, and completion claims. Two detail pages own the mechanisms this page once carried in full: [Pack Preview And Archive Contents](pack-preview-and-archive-contents.md) answers which files a pack command selects and which files an archive actually contained, and [Consumer Resolution And Declarations](consumer-resolution-and-declarations.md) answers why a packed subpath fails to resolve and whether declarations match the runtime target it loads.

## Identify The Delivered Contract

Treat a package as both metadata and selected files. In Node.js, the nearest package `type` and `.mjs`/`.cjs` extensions affect module interpretation; `main` identifies a primary entry, while `exports` can define public subpaths and conditional entry points. When present, `exports` takes precedence over `main` for package-name resolution and blocks unlisted subpaths. Introducing or changing it can break consumers that relied on previously reachable paths. Package `files`, ignore rules, and packager-specific inclusion behavior determine what is delivered; a working tree is not the package artifact.

Treat explicit `type` and `.mjs`/`.cjs` markers as the clearest Node.js module-format evidence, not as an exhaustive rule for every `.js` file. The [Node.js packages page](https://nodejs.org/api/packages.html#syntax-detection) labels syntax detection Stability 1.2 (Release candidate) and describes ambiguous `.js` input without an explicit marker as potentially detected as ESM when it contains ESM-only syntax. The snapshot consulted for this page identified itself as Node.js v26.13.1, and the unversioned URL can serve a later release. Check the target Node version and actual invocation before interpreting a package's `.js` entry. Do not infer Bun's behavior from this Node-specific rule.

A TypeScript package whose `files` allowlist names only `dist`, while the checkout also contains `src/*.ts`, delivers built files rather than sources. The delivered contract is answered by the archive plus the fields that describe the emitted output: a top-level `types` field or an `exports` `types` condition naming declaration files, and `main` or an `exports` `import` target naming the emitted JavaScript. Ask what the package delivers, not what the checkout contains; the selection mechanics behind that answer belong to [Pack Preview And Archive Contents](pack-preview-and-archive-contents.md).

An illustrative export map for such a package. Target names and declaration layout must match the package's actual emitted artifact and supported consumers:

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

This example declares only an `import` runtime branch; it does not imply CommonJS support. If a package claims `require` support, validate its `require` target and matching declarations as a separate consumer surface. TypeScript's accepted `types` conditions and Node's runtime conditions are not interchangeable. Branch shapes, condition order, and declaration wiring belong to [Consumer Resolution And Declarations](consumer-resolution-and-declarations.md).

Check every declared artifact surface that the request names:

- Runtime entry points and supported subpaths, including relevant `import` or `require` conditions.
- Emitted JavaScript formats and file locations, with package metadata consistent with those outputs.
- Type declarations and their association with the runtime entry points when declarations are part of the package contract.
- Executable `bin` files, assets, or other consumer files only when the package declares or requires them.
- The target runtime and version, distinct from the manager used to install or build the package.

Do not assume that a manifest field guarantees the referenced file exists in the packed artifact. A format label or successful type check does not prove that the consumer can load the artifact.

## Distinguish Build, Pack, And Publish

A build produces configured output; packing selects files and creates or previews a distribution artifact; publishing sends an artifact to a registry. These are separate outcomes, and none of them establishes another. A project may publish source, generated output, or another selected file set according to its own contract. No single layout, build tool, or dual-format output is universal.

What a named packer selects, whether its preview runs lifecycle hooks, and what the resulting archive contains are packer contracts scoped to the manager and version that state them; they are not JavaScript or TypeScript language behavior. [Pack Preview And Archive Contents](pack-preview-and-archive-contents.md) owns those mechanics for npm and Bun, including the interaction of `files`, ignore files, and lifecycle scripts, and why a preview is a listing rather than an artifact. Confirm the target packager's behavior and version there instead of extending one manager's documented rules to another.

Do not infer that local pack success proves publication, registry permissions, authentication, remote installation, or registry-side attestations. Publishing and registry administration require separate explicit authority and remain outside this skill's scope. A pack result and a publish result are different evidence, and neither one closes the consumer question in the next section.

## Test The Actual Consumer When Requested

When the request includes package-consumer validation, prefer the artifact path that consumers will receive. A useful bounded check may inspect a dry-run file list, create the tarball, install that tarball in an isolated fixture, and exercise specified entry points. This combination is an evidence strategy, not a universal package test protocol.

Keep the result scoped:

- A source-tree test does not establish that packed files include all required output.
- A symlinked workspace or local package directory is not equivalent to a packed tarball.
- A local tarball install does not test remote registry publication, access controls, or registry attestations.
- One successful import does not establish every conditional export, subpath, module format, runtime, or version.
- Type declarations may resolve while the corresponding runtime file is absent, or vice versa; test each surface required by the contract.

Use only the project's configured build and package tools unless the request authorizes another path. Keep the consumer fixture isolated and disposable only when its creation and cleanup are authorized. Report the exact entry points, conditions, runtime, versions, commands, and artifact examined; identify untested surfaces explicitly.

[Consumer Resolution And Declarations](consumer-resolution-and-declarations.md) owns the ordered four-layer diagnosis for a failing packed subpath, the install-and-check chain against the archive, and the declaration-resolution question. This page owns the scope of the evidence; the documented layer order does not let one layer's pass stand in for another.

## Preserve Scope And Compatibility

Treat `name` and `version` as package identity metadata where the selected registry or packager requires them. Registry immutability and unpublish rules are registry-specific; npm's public-registry policies do not define every compatible registry. Registry tags, signatures, integrity metadata, and provenance have distinct meanings and depend on the client and registry. Integrity checks associate artifact bytes with digests; provenance describes build or publishing context and is not proof that code is harmless.

Keep type checking, transformation, bundling, declaration generation, and runtime execution distinct. A build tool can emit files without checking types; a checker can pass without proving the emitted files load. Match package conditions and output formats to the consumer evidence available, and state when a claim is documentation-based rather than exercised against the target artifact.

The versions cited here are bounded rather than current-by-default. The npm statements are npm CLI v12 or the version named beside them; the TypeScript and Bun documentation is rolling; the Node.js packages claim is pinned to the page snapshot that identified itself as Node.js v26.13.1 while the unversioned URL can move to a later release. Verify the exact compiler, runtime, and packager versions and options for the target. Local tarball checks do not establish remote publication or broad compatibility across runtimes, versions, or module formats.

For npm specifically, the [npm CLI v12 `npm publish` documentation](https://docs.npmjs.com/cli/v12/commands/npm-publish/) describes publication and points to file-selection rules; the selection details and their npm-version scope are on the pack preview page. The [Node.js packages documentation](https://nodejs.org/api/packages.html) documents `exports` encapsulation, condition selection, and package module interpretation. The [TypeScript Modules Reference](https://www.typescriptlang.org/docs/handbook/modules/reference.html#packagejson-exports) explains how supported module-resolution modes follow `exports` and locate type files. These links explain mechanisms, not compatibility guarantees or executed evidence.

A framework build's emitted application output is not a package tarball; the invocation-to-consumer chain for framework output belongs to `node-project-reference -> reference/framework-output-and-consumers.md`. This page and its two detail pages cover package artifacts and consumer evidence only: publication, registry administration, release governance, and deployment stay outside the operation.

Do not select Vite as a tool, default, or supported workflow, or rely on a Vite-based workflow. This direct-use boundary is not a blanket ban on every transitive Vite package and does not establish that any project graph is Vite-free. A framework or test workflow that invokes or relies on Vite is not a no-Vite workflow; project-specific dependency-graph claims require exact versions and resolved-tree evidence.
