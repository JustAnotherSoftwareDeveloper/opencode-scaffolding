# Pack Preview And Archive Contents

Use this reference when a request asks which files a pack command would deliver, which files an archive actually contained, or which lifecycle step changed the result. It owns pack-selection and archive-content evidence for a TypeScript package built for Node.js or Bun. [Artifact And Consumer Boundaries](artifact-and-consumer-boundaries.md) owns the delivered contract and the build, pack, and publish separation; [Consumer Resolution And Declarations](consumer-resolution-and-declarations.md) owns runtime export and declaration resolution. Node.js and Bun mechanics appear only where they explain how TypeScript build output reaches a package archive. JavaScript-only packages are out of scope, and a JavaScript-only request is reported as out of scope.

File selection, ignore precedence, hook order, and dry-run semantics are manager contracts stated by their publishers, not JavaScript or TypeScript language behavior. Keep the package manager, its version, the command, and the selected package or workspace beside every statement, and never transfer a result from npm to Bun or from one version to another.

## Read A Preview As A Selection Contract

A pack preview answers a narrower question than the request often implies: which files the named packer expects to select, from the named working directory, for the named package or workspace, at the named packer version. Compare a preview and an archive on the same terms, or the comparison establishes nothing:

- **Working directory and selected package.** Record the directory the command ran in, the package or workspace it selected, and the flags that decided that selection. In a monorepo these are distinct facts.
- **Packer and version.** Record `npm` versus `bun`, the exact version, and the subcommand. `npm pack` and `npm run pack` are also different command paths.
- **Prospective file list.** A dry run reports what the manager would select. It is a listing, not an artifact.
- **Actual archive.** The `.tgz` is the file a consumer receives; inspect its member list and its manifest, not the working tree.
- **Lifecycle effects.** Hooks may have generated, moved, or removed files before selection, and the preview may or may not have run them.

For npm, the CLI v12 pack page documents `npm pack --dry-run` as a prospective contents report and `npm pack` as creation of a tarball ([npm pack](https://docs.npmjs.com/cli/v12/commands/npm-pack/)). The npm CLI v11 pack page likewise describes `--dry-run` as reporting what would be done without making the change ([npm pack, v11](https://docs.npmjs.com/cli/v11/commands/npm-pack/)); that publisher sentence does not state whether pack hooks run, so it cannot be read as a no-side-effects promise. A dry-run listing is not the archive, and neither the listing nor the working tree proves that an archive installs or that a consumer can load it. A preview also says nothing about files that an install-time script creates in a consumer's tree; those effects happen after extraction and are not archive members.

Bun implements its own packer. `bun pm pack` is Bun's command, not npm execution running under a Bun label, and the current Bun command page documents `--dry-run` as doing the pack tasks except writing the tarball, plus its own `--ignore-scripts` control ([Bun pm](https://bun.com/docs/pm/cli/pm)). The same page says Bun follows the same rules as `npm pack`; that sentence is publisher-stated compatibility prose, not a cross-implementation test. The inspected Bun repository implements its own include and exclude walk with its own default ignore patterns, which visibly include entries such as `.env.production` and `bunfig.toml` ([Bun pack command source](https://github.com/oven-sh/bun/blob/main/src/runtime/cli/pack_command.rs)). Treat the shared field names as shared vocabulary, not as parity: the two packers may agree on ordinary cases, but no claim here says they select identical files, run identical hooks, or accept identical options. Verify the installed packer and version instead of extending one manager's page to the other.

## Trace An Omitted Checkout File

An npm package archive is a computed selection. The `files` field acts as an allowlist when present; when it is absent, npm applies its default selection instead ([npm package.json](https://docs.npmjs.com/cli/v12/configuring-npm/package-json#files)). `package.json`, README and readme variants, license or licence or copying files, and the targets configured through `main` and `bin` receive special required treatment, so a mandatory file can appear even when the allowlist does not name it. Ignore rules cut in both directions: a root `.npmignore` does not override the `files` allowlist, but a nested ignore file can exclude a subtree that the allowlist admitted. Where no `.npmignore` exists at a level, `.gitignore` can supply fallback exclusions, and `.npmignore` takes priority over `.gitignore` at the same level.

Several exclusions and exceptions prevent a one-line summary. VCS metadata, `.npmrc`, and ordinary root `node_modules` are excluded, while `package-lock.json` is excluded but `npm-shrinkwrap.json` remains packable, so "all lockfiles are excluded" is wrong. Declared `bundleDependencies` or `bundledDependencies` can place dependency package files under the archive's bundled dependency paths, so "`node_modules` is never included" is also wrong. npm's documented selection does not generally traverse symlinks as package content.

Consider a TypeScript package whose checkout contains its source, its built output, and a nested ignore file:

```text
package.json
tsconfig.build.json
src/index.ts
src/feature.ts
dist/index.js
dist/index.d.ts
dist/feature.js
dist/.npmignore          # excludes feature.js
```

```json
{
  "name": "widget",
  "scripts": {
    "build": "tsc -p tsconfig.build.json",
    "prepack": "npm run build"
  },
  "files": ["dist"]
}
```

The build emits `dist/index.js`, `dist/index.d.ts`, and `dist/feature.js` from the TypeScript sources. The `files` allowlist admits `dist`, the nested `dist/.npmignore` removes one admitted file, and the resulting archive lists:

```text
package.json
README.md
dist/index.js
dist/index.d.ts
```

`src/feature.ts` is absent because the allowlist never admitted `src`. `dist/feature.js` is absent even though it exists in the checkout and inside `dist`, because the nested ignore file constrained that subtree. `package.json` and `README.md` appear because npm treats them as required, not because the allowlist named them. The source tree cannot answer the archive question: the same checkout produced one set of files before packing and a smaller set inside the artifact.

Traces of this shape are the usual explanation for a consumer report that a file "is in the build". Inspect the allowlist, then the ignore files at and below the candidate directory, then the actual tarball. Do not add a file to the export map to compensate for a file that packing never selected.

## Run And Gate The Pack Lifecycle

npm's scripts documentation lists `prepack`, `prepare`, and `postpack` for `npm pack`, and states that `prepare` also runs in other operations such as local install and Git dependency preparation, so it is not pack-exclusive ([npm scripts](https://docs.npmjs.com/cli/v12/using-npm/scripts)). The `prepare` or `prepack` hook is one available place to compile TypeScript into `dist`; it is not a requirement, and a package can ship prebuilt output instead.

`npm run pack` is not `npm pack`. The first invokes the explicitly named `pack` script in `package.json`; the second is the npm CLI packing command. Both can coexist in one manifest, and a successful `npm run pack` says nothing about what the CLI would select or write.

Pinned implementation and a bounded run on Node.js v24.18.0 with npm 11.16.0 (`libnpmpack` 9.1.9, `pacote` 21.5.0, and `npm-packlist` 10.0.4) show where the gates sit. `prepack` and `prepare` are gated on `ignoreScripts`, not on `dryRun`; the tarball write alone is gated on `dryRun === false`, and `postpack` runs after the archive is formed ([libnpmpack source](https://raw.githubusercontent.com/npm/cli/v11.16.0/workspaces/libnpmpack/lib/index.js), [pacote directory fetcher](https://raw.githubusercontent.com/npm/cli/v11.16.0/workspaces/pacote/lib/dir.js)). In an authored fixture, ordinary pack, `--dry-run`, and `--ignore-scripts` each exited 0. Ordinary and dry-run runs produced `prepack`, `prepare`, and `postpack` traces; the ignore-scripts run produced none. Ordinary pack wrote a `.tgz` and its archive captured the hook mutations; dry-run wrote no tarball. npm also wrote cache and debug-log artifacts in the scratch location it was given. On that route, a dry run is not an inert guarantee: it avoids the tarball, not the hooks, and hook or manager side effects can still occur.

Do not invert that evidence either. The npm publisher pages do not explicitly state hook behavior under `--dry-run`; the implementation and the bounded run establish it for that version. A different npm release can gate differently, and a manager other than npm need not share the gates at all.

The hook gates are also not the only way a preview and an archive diverge. In a second authored fixture, a `prepare` hook read `npm_config_dry_run` and wrote `dry-generated.txt` during the dry run while ordinary pack wrote `normal-generated.txt`; each command selected its own hook output. That demonstrates a possible conditional divergence, not a default one. The general consequence is stable: when hooks can inspect the command, the prospective list describes that hook path's output, and only the archive describes the ordinary run's bytes.

`--ignore-scripts` needs the same precision. In the controlled fixture, `npm --ignore-scripts run pack` exited 0, ran the explicitly requested `pack` script, and suppressed that script's lifecycle pre/post hooks. The flag does not mean "do not run the explicitly requested script"; for npm it controls package scripts around an invocation, and the explicit `npm run` target still executes.

Bun's controls belong to Bun. Its command page documents `--ignore-scripts` for `bun pm pack` as skipping `prepack`, `prepare`, and `postpack`, and `--dry-run` as previewing without writing the tarball. On installed Bun 1.3.14, authored fixtures produced `prepack`, `prepare`, and `postpack` traces for ordinary pack and for `bun pm pack --dry-run`, no trace for `bun pm pack --ignore-scripts`, and an archive only in the ordinary and ignore-scripts runs. That is a bounded observation of one release, not a Bun version matrix, and it is not evidence about npm's gates. The commands exercised on those tested routes were:

- `npm pack --json`
- `npm pack --json --dry-run`
- `npm pack --json --ignore-scripts`
- `npm --ignore-scripts run pack`
- `bun pm pack`
- `bun pm pack --dry-run`
- `bun pm pack --ignore-scripts`

## Decide Whether A Dry Run Or Suppression Omits Output

A missing generated file in a preview normally has two different causes, and the scripts decide which one applies. Suppose `dist` is empty in the checkout and `prepack` runs the TypeScript build. With hooks enabled, `npm pack --dry-run` runs `prepack`, the compiler writes `dist`, and the prospective listing includes `dist/index.js`. With `--ignore-scripts`, the same command skips the hook, no compiler runs, and the listing contains no `dist` output at all. Ordinary pack with hooks then writes a tarball whose members include `dist`, while the suppressed preview never represented that archive.

Three consequences follow:

- A preview that omits generated output can be a hook-gate fact, not an allowlist fact. Inspecting `files` and ignore rules first would misdiagnose it.
- A hook that builds into the checkout mutates the working tree even under dry-run in the tested npm and Bun versions. Inspect the relevant scripts before invoking either form and decide whether those writes are authorized.
- Suppressing hooks that create required output changes the selected set. Do not suppress them "for safety" when the build is what the archive needs; instead confirm what the hooks do and whether running them is permitted.

Where a request needs the delivered file set, the archive is the evidence. The preview is a cheaper question answered earlier, and comparing a preview with an archive is informative only when both were produced under recorded commands and versions, because hooks can branch, reorder, or disappear between them.

## Start The Packed-Subpath Diagnosis At Packing

When `import { parse } from "widget/feature"` fails for a consumer that installed the archive, do not treat the failure as one diagnosis. The canonical four-layer diagnosis lives in [Consumer Resolution And Declarations](consumer-resolution-and-declarations.md); this page owns its first layer only: whether the intended public target is in the archive the consumer received.

A target missing from the archive is a packing fact. The questions that follow are packaging questions: was the file inside the allowlisted directory, did a nested ignore or a strict exclusion remove it, did a lifecycle-gated build even produce it, and did the command select the package or workspace that owns it. A dry-run listing can point at those questions, but only the tarball settles them, and a source-tree or linked-workspace file never does. Editing `exports` cannot add a file to an archive, and no declaration file can repair absent runtime content. Once the target is confirmed present, continue with export-map, loader, and declaration layers on the page that owns them.

## Diagnose A Workspace Pack

The observable: a root-level workspace pack produces a tarball that installs, but generated files the package needs are missing, even though the same package works when imported from the linked workspace. The linked import resolves by symlink to the source package directory, where `dist` exists and development metadata applies. The archive was produced from whichever package and directory the pack command actually selected, and that selection or its hooks did not produce or include `dist`. The import success and the archive failure are therefore evidence about different artifacts, not about `exports` or the consumer.

Diagnose in this order: record the working directory, the workspace flags, the resolved package name and path, the packer and version, and the tarball path; inspect the packed member list; then compare allowlist, ignore files, and lifecycle hooks for the selected package. npm CLI v12 documents `--workspace`, `--workspaces`, and `include-workspace-root` for monorepo package selection, so a root command can intentionally or unintentionally choose a different package or add the root package. Those option names are npm's documented interface; do not assume Bun accepts the same flags or resolves workspace roots the same way, and verify Bun's own command on the installed version.

Do not "fix" this by pointing the consumer at the workspace path or by adding files to the export map. Report the selected package, the archive members, the hook conditions, and the missing path. Any change to workspace scripts, build output, or package metadata needs the relevant owner and authorization.

## Keep Publisher Limits Visible

- **npm is version-scoped.** The `--dry-run`, `--ignore-scripts`, lifecycle, and workspace-option statements belong to the npm CLI documentation version cited. The observed hook behavior belongs to npm 11.16.0 on Node.js v24.18.0, not to every npm release, and the v12 page's exact patch was not surfaced.
- **Lifecycle behavior varies by manager and command.** `prepare` runs outside packing. `npm pack`, `npm run pack`, and `bun pm pack` are three paths with three contracts. Bun's `--ignore-scripts` is documented for pack hooks; npm's flag has a broader package-script role while still letting an explicitly requested script run. Do not merge the families into one rule.
- **Bun's pages are rolling and partly contradictory.** Bun's command page carries no surfaced release version, its pack compatibility sentence is publisher prose, and Bun's documentation set elsewhere contradicts itself about declaration generation. Its repository is mutable `main`. No statement here treats Bun's documentation as a settled matrix for an untested release.
- **A preview is not a consumer or publication result.** Neither a dry-run listing nor a local archive proves installation behavior, registry publication, access control, attestation, or compatibility across runtimes and versions.
- **Evidence qualification is part of the page.** Where the available publisher pages or named-version observations do not support a stronger statement, this page keeps an explicit qualified limit instead of a deferred note; nothing here is waiting on a separate authoring task. Verify the installed manager and version before applying any of it.

## Keep Ownership And Authorization Explicit

This page owns package artifact inspection: selection, archive members, lifecycle effects, and the packing layer of a failure. Build-script and production-output changes route to the production owner (`node-project-writer`); dependency, manager, runtime, and installation changes route to `node-project-dependencies`; source style and API design route to the passive style guidance. Diagnosis is not repair, and a finding here does not authorize a change.

Nothing in this reference authorizes execution. Running a pack command, a dry run, or a lifecycle hook can execute package scripts, write build output, mutate the checkout, and create tarballs, caches, and logs. Inspect the scripts first, confirm that the working directory and workspace selection are the intended target, run only what the request permits, and report created or modified paths. Do not clean or overwrite generated files without permission. Publication, registry administration, release governance, and deployment remain outside this operation.

## Cross-Links For The Surrounding Questions

- Delivered contract, metadata expectations, and the build, pack, and publish separation: [Artifact And Consumer Boundaries](artifact-and-consumer-boundaries.md).
- Canonical four-layer packed-subpath diagnosis, export-map branches, and declaration resolution: [Consumer Resolution And Declarations](consumer-resolution-and-declarations.md).
- Dependency, manager, runtime, and installation changes: `node-project-dependencies`.
