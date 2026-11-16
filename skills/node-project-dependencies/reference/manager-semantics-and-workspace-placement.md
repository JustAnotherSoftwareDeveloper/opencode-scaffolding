# Manager Semantics And Workspace Placement

## Scope

For the selected package manager and version, this page states how dependency groups,
peer and optional dependencies, workspace membership, lockfiles, and install commands
are documented to behave. The subject is TypeScript source, configuration, declarations,
tests, quality diagnostics, and package artifacts in Node.js or Bun projects. Standalone
JavaScript guidance, `allowJs` and `checkJs` checking, and JSDoc typing of `.js` files
are outside this reference; a JavaScript-only request is out of scope.

Four layers stay separate. The manifest declares intent; the lockfile records one
manager's resolved graph; an install produces a physical layout; an invocation starts a
particular executable. This page states documented manager behavior for those layers. It
does not read a project's mixed evidence trail. Clue-to-executable interpretation belongs
to `node-project-reference -> reference/manager-workspaces-and-invocation.md`, and the
canonical mixed manager-and-runtime case belongs to
`node-project-reference -> reference/runtime-and-project-structure.md#reconcile-mixed-runtime-clues`.

Each manager section is a summary of what the named publisher page documents for the
named version or page generation. These are not defaults, recommendations, compatibility
conclusions, or tested cross-manager comparisons. The group names `dependencies`,
`devDependencies`, `optionalDependencies`, `peerDependencies`, and `peerDependenciesMeta`
are shared manifest vocabulary; the shared words do not establish a shared install,
peer-resolution, workspace-linking, lockfile, or lifecycle contract.

Reading a mechanism here is documentation, not authorization. Preflight and examples on
this page do not authorize installing, resolving, rewriting a lockfile or manifest,
migrating a manager, or running lifecycle scripts; those effects need the dependency
owner's evaluation and an explicit request.

## Version Scope To Read First

- **npm** documentation is pinned to CLI v12 in its URL paths. The inspected pages do not
  expose a patch version or an update date, so a statement here covers the v12 page, not
  every npm generation.
- **pnpm** documentation is mostly unversioned at current paths. Its v12 release notes
  state that v12 is stable and that the documentation applies to pnpm 11 and 12, while
  individual features name versions such as the v12.7.0 workspace conversion
  ([what's different in pnpm 12](https://pnpm.io/blog/whats-different-in-pnpm-12)).
- **Yarn Modern** pages are unversioned; a manifest example uses `yarn@4.0.0` as an
  illustration, not a page pin ([manifest, Yarn](https://yarnpkg.com/configuration/manifest)).
  **Yarn Classic** pages identify Yarn 1 and are a separate generation, not
  interchangeable with Modern.
- **Bun** package-manager pages are rolling and name versions only for particular changes,
  such as the text `bun.lock` default in v1.2 and pre-v1.3.2 linker-default context
  ([Bun lockfile](https://bun.com/docs/pm/lockfile)). Their absence of a version label is
  not evidence of the installed release.

## Dependency Groups And Peer Mechanics

### npm CLI v12

npm v12 documents `dependencies` as name-to-range or other supported specs, and gives
distinct purposes to `devDependencies`, `optionalDependencies`, `peerDependencies`, and
`peerDependenciesMeta` ([package.json, npm CLI v12](https://docs.npmjs.com/cli/v12/configuring-npm/package-json/)).
Peers are installed automatically by default, while an optional peer is not installed
automatically. An optional dependency's install failure need not fail the install, so the
consuming code must handle the dependency's absence. `overrides` are read from the root
manifest, not from installed dependencies or workspace manifests.

### pnpm

pnpm uses the familiar group names and adds manager-specific settings. Peer installation
is governed by `autoInstallPeers`, which the current peer-settings page documents as
enabled by default; optional peers have separate behavior, and peer-dependent packages
can be deduplicated or represented in context-specific variants, with workspace peer
reuse documented alongside `dedupePeerDependents`
([peer dependency settings](https://pnpm.io/settings/peer-dependencies)). Root `overrides`
live in workspace settings and accept selectors that distinguish dependency groups and
peers ([dependency resolution settings](https://pnpm.io/settings/dependency-resolution)).
`packageManager` and `devEngines.packageManager` have documented selection and recording
behavior, while `devEngines.runtime` is an explicit runtime-pinning feature and not
something an ordinary install reveals about the executing application
([package.json, pnpm](https://pnpm.io/package_json)).

### Yarn Modern

Modern Yarn documents `devDependencies` as needed when a package is installed as a
workspace, optional dependencies with OS, CPU, and libc conditions, and peer dependencies
as inherited from an ancestor so that the consumer can provide a shared instance. It also
documents a peer-with-default case when the same item appears in both `dependencies` and
`peerDependencies`, and keeps `resolutions` a root manifest field
([manifest, Yarn](https://yarnpkg.com/configuration/manifest)).

### Yarn Classic (Yarn 1)

Yarn Classic's archived pages describe development-only dependencies, optional
dependencies whose absence does not stop installation, and peer dependencies as a
compatibility declaration whose missing-peer warning can be suppressed with
`peerDependenciesMeta.optional`. The same page documents bundled dependencies
([package.json, Yarn Classic](https://classic.yarnpkg.com/en/docs/package-json/)). A flat
Classic install can write a `resolutions` field. These roles are the Yarn 1 pages' own
semantics and do not describe Modern behavior.

### Bun

Bun's install page states that it installs `dependencies`, `devDependencies`, and
`optionalDependencies`, and installs peer dependencies by default. `bun add` writes to
`dependencies` unless a group flag is supplied, with peer behavior and group moves
documented separately ([bun install](https://bun.com/docs/pm/cli/install);
[bun add](https://bun.com/docs/pm/cli/add)). Bun states that it accepts npm's `overrides`
and Yarn's `resolutions`. Lifecycle handling is policy-bearing: `trustedDependencies`
changes whether an installed dependency's lifecycle script runs, and project lifecycle
scripts and dependency lifecycle scripts have different documented treatment. Install
strategy and linker defaults depend on project and lockfile context, including the
pre-v1.3.2 project context named on the install page.

### Override Fields Are Not Interchangeable

npm documents root-only `overrides`; pnpm documents root `overrides` with group- and
peer-aware selectors; Yarn Modern has a root-only `resolutions` field; Yarn Classic's flat
install can write `resolutions`; Bun accepts both npm and Yarn names. Similarly named
controls are not documented to share matching or resolution semantics, so read the
selected manager's page rather than translating a field name.

## Lock And Install Guarantees By Manager And Command

A command label such as install, `ci`, immutable, or frozen does not carry one
cross-manager write set. Read the manager, version, command, and configuration together,
then read the effect on the manifest, lockfile, installed tree, and scripts.

- **npm v12 install and clean install.** `npm install` uses a satisfying `package-lock.json`
  resolution and updates the lock when manifest ranges require a new resolution; the
  install page also states that `package-lock.json` takes precedence over `yarn.lock` when
  npm considers both ([npm install](https://docs.npmjs.com/cli/v12/commands/npm-install/)).
  `npm ci` instead requires an existing matching lock, fails rather than updating it,
  removes an existing `node_modules`, and does not write `package.json` or
  `package-lock.json`; tree-shaping options used to create the lock may need to be
  repeated ([npm ci](https://docs.npmjs.com/cli/v12/commands/npm-ci/)). Both commands can
  install, so "did not rewrite the lock" is not the same as "changed nothing".
- **pnpm install.** The install page states that an existing lock is frozen by default in
  CI, that an install covers all workspace projects by default unless filtered, and that
  `--lockfile-only` updates `pnpm-lock.yaml` and `package.json` without `node_modules`
  writes, while `--dry-run` previews without those writes
  ([pnpm install](https://pnpm.io/cli/install)). The lockfile page describes importer,
  package, and snapshot records and a possible two-document lockfile whose documents each
  carry `lockfileVersion` ([reading pnpm-lock.yaml](https://pnpm.io/lockfile)).
- **Yarn Modern install.** Install is documented as resolution, fetch, link, then build.
  `--immutable` covers lockfile changes and `--immutable-cache` covers cache changes, with
  immutable installs enabled by default on CI; exact version preference is stated not to
  be standardized outside ordinary semver guarantees
  ([yarn install](https://yarnpkg.com/cli/install)). Lockfile immutability and cache
  immutability are separate guarantees.
- **Yarn Classic install.** A sufficient `yarn.lock` installs the recorded exact versions
  without checking for newer ones; an absent or insufficient lock leads to resolution and
  a lockfile update. `--frozen-lockfile` prevents updates and fails when one would be
  needed ([yarn install, Yarn Classic](https://classic.yarnpkg.com/en/docs/cli/install/)).
  Classic workspaces share one lockfile.
- **Bun install and update.** The text `bun.lock` became the default in v1.2. Current docs
  say `--frozen-lockfile` installs recorded versions and fails on a specified
  manifest/lock disagreement, but it is not automatically enabled in CI; `--production`
  implies it and does not remove `devDependencies` already present from an earlier install
  ([bun install](https://bun.com/docs/pm/cli/install)). When no `bun.lock` is present, Bun
  documents lockfile migration with an order across recognized lockfiles and preserves
  the original file ([Bun lockfile](https://bun.com/docs/pm/lockfile)). `bun update` is a
  separate resolution-changing command: it updates direct and transitive dependencies to
  versions allowed by their requesting ranges and rewrites `package.json` and `bun.lock`,
  with `--latest` documented as ignoring the ranges
  ([bun update](https://bun.com/docs/pm/cli/update)).

## Workspace Declarations Do Not Establish Equivalent Membership

- **npm v12** reads root `workspaces` globs and, during install, symlinks each matched
  workspace package into the root `node_modules`; the workspace page documents adding a
  dependency to a workspace and running commands scoped to workspaces
  ([npm workspaces](https://docs.npmjs.com/cli/v12/using-npm/workspaces/)).
- **pnpm** ordinarily requires a root `pnpm-workspace.yaml`. The `workspace:` protocol can
  require resolution to a local workspace package rather than a registry package. The
  current page annotates conversion from a root manifest workspace list, when no pnpm
  workspace file exists, as added in pnpm v12.7.0; that is a versioned conversion path,
  not a generic rule for earlier releases
  ([pnpm workspaces](https://pnpm.io/workspaces)).
- **Yarn Modern** reads root `workspaces` globs, documents `workspace:` references with
  publish-range rewriting, and supports focused installs and workspace script execution
  ([Yarn workspaces](https://yarnpkg.com/features/workspaces)).
- **Yarn Classic** reads a root workspace declaration and documents a single lockfile, a
  hoisted layout, and local linking when a dependency range matches
  ([Yarn Classic workspaces](https://classic.yarnpkg.com/en/docs/workspaces/)).
- **Bun** documents root `workspaces` globs including negative patterns, a required
  package name for a matched workspace, workspace filtering, and install across all
  workspaces by default. It also permits workspaces outside the root directory, subject
  to the documented path and lifecycle effects
  ([Bun workspaces](https://bun.com/docs/pm/workspaces)).

Workspace syntax therefore does not establish equivalent membership or linking. Selection,
linking, hoisting, lockfile scope, filtering, and publish-time rewriting differ by manager
and version. A repository's `packages/*` declaration does not tell you which directories
another manager would treat as members, link, expose, or script.

Membership is also not runtime. A package-manager install does not identify the executing
runtime: Bun documents `bun install` as usable in existing Node.js projects, which
establishes Bun's capability as a package manager and says nothing about the process that
runs the application. pnpm's `devEngines.runtime` is an explicit runtime pin, not an
inference available from an ordinary install.

### Two Candidate Questions

**Should this package go in one workspace package or in every package?** Start from who
imports the API at build or run time. The edge belongs in that package's dependency group;
the root workspace declaration only decides membership. Add the declaration to the target
package, then use the manager's workspace selection to run the check or install for that
package: npm documents `--workspace` filtering, pnpm documents `--filter`, Bun documents
workspace filters, and Modern Yarn documents focused installs and `workspaces foreach`.
Adding a package to every member to make one package's command resolve hides a placement
question rather than answering it, and it changes every member's manifest.

**Is this a local workspace member or a registry resolution?** A version range alone does
not answer it. npm symlinks a matched workspace package during install; pnpm's `workspace:`
can require local resolution; Modern Yarn documents `workspace:` references and publish-range
rewriting; Classic links locally when a range matches; Bun documents `workspace:`
references. Check the declared protocol or range, the selected manager and version, and
the importer entry in that manager's lockfile before calling the dependency local or
remote.

## The npm v12 And Bun Lockfile Wording Conflict

The two publishers do not align on `npm-shrinkwrap.json` at the npm v12 boundary, and this
page does not decide which source is stale. npm CLI v12's package-lock page states that, as
of v12, npm no longer reads or writes `npm-shrinkwrap.json`, including a dependency-tarball
shrinkwrap ([package-lock.json, npm CLI v12](https://docs.npmjs.com/cli/v12/configuring-npm/package-lock-json/)).
Bun's lockfile page states that Bun migrates that file, prefers it over `package-lock.json`
when both are present, and does so "as npm does"
([Bun lockfile](https://bun.com/docs/pm/lockfile)). The inspected pages do not reconcile
whether Bun's wording reflects older npm behavior, a different reading, or documentation
drift, and the "as npm does" phrase cannot establish identical import graphs.

Lockfile format versions have a related, unresolved shape. npm v12's package-lock page
lists versions 1, 2, and 3, and its config page allows those values with v3 as the default
when no lock exists ([npm config](https://docs.npmjs.com/cli/v12/using-npm/config/)).
npm v12's `.npm-extension` page separately requires `lockfileVersion: 4` for extension
state ([.npm-extension, npm CLI v12](https://docs.npmjs.com/cli/v12/configuring-npm/npm-extension/)).
Bun's importer lists npm lockfile versions 2, 3, and 4. The pages do not explain whether v4
is a feature-specific exception, which npm release or configuration emits it, or how it
relates to the v1-to-v3 list.

The consequence is procedural. Record the npm version, the lockfile name, the
`lockfileVersion` field, and which command reads the file. Treat `lockfileVersion` as a
field to qualify, not as a cross-tool compatibility promise, and do not delete, regenerate,
or edit either lockfile to resolve the disagreement.

## Preflight A Requested Install Or Lock Change

Run this preflight before proposing or performing any effect. It produces a bounded
description of the action; it does not authorize the action.

1. **Name the manager and version.** Record the declared selection, such as
   `packageManager`, and the version actually printed by the manager in the same shell.
   A declaration alone does not prove the active executable.
2. **Name the workspace root and target package.** Read the nearest manifest above the
   work, the root workspace declaration, and the lockfile the manager computes for that
   root. A package directory inside a workspace is not automatically the install root.
3. **Read the existing lockfile and configuration.** Record the lockfile name and
   `lockfileVersion`, plus settings that change selection or effects for this manager:
   peer installation, linker or install strategy, frozen or immutable defaults,
   production and omitted groups, trusted lifecycle scripts, and workspace filters.
4. **Classify the requested action.** Separate a lock-currency check that must not rewrite
   the manifest or lock, a resolution or update that rewrites the lock and possibly the
   manifest, and an install or sync that creates or removes an installed tree.
5. **Name the effects the action may produce.** State which files, lock records, installed
   directories, symlinks, cache entries, and lifecycle scripts may change, and for which
   command. A frozen or immutable label does not itself describe the write set.
6. **Confirm authorization and the post-action evidence.** Identify the exact command,
   package scope, target platform, and versions before running anything, then inspect the
   diff and installed state afterward and run only authorized checks.

## Examples

### A Development Compiler In One Workspace Consumed Through A Local Link

Consider a repository whose root manifest declares `"workspaces": ["packages/*"]`. One
workspace owns a development-only TypeScript compiler and a command that uses it:

```json
{
  "name": "@repo/tooling",
  "devDependencies": { "typescript": "^6.0.0" },
  "scripts": { "check": "tsc -p tsconfig.json --noEmit" }
}
```

A second workspace consumes that local package and runs its command:

```json
{
  "name": "@repo/site",
  "dependencies": { "@repo/tooling": "workspace:*" },
  "scripts": { "check": "repo-check --project tsconfig.json" }
}
```

`@repo/tooling` provides the `repo-check` command from its own package. The `workspace:`
spelling applies where the selected manager documents it; npm documents auto-symlinking
matched workspace packages during install, and Classic links locally when a range matches.
The edge questions are separate and answerable only from the manifests and the lockfile:
`@repo/site` records the local edge to `@repo/tooling`, `@repo/tooling`
records the compiler edge, and the root lockfile records both resolutions for the manager
that wrote it. The layout then decides whether `site`'s command can reach the compiler
binary; the manager's linking and hoisting behavior, not the manifest text, produces that
reachability.

A second manager may accept the same text and link, hoist, or expose the binary
differently, so a successful `site` check does not show where the compiler edge lives.
Read the two manifests, the lock importer for each package, and the installed layout
before describing the dependency graph.

### A Read-Only Lock-Currency Check Compared With An Install That Rewrites The Lock

Suppose the question is only whether the checked-in lock still satisfies the manifests.
Use the selected manager's documented non-rewriting mode and record which command ran:
`npm ci` requires a matching lock and fails rather than updating it, while still replacing
the installed tree; pnpm's CI behavior freezes an existing lock; Modern Yarn's `--immutable`
covers lockfile changes; Classic's `--frozen-lockfile` fails when an update would be
needed; Bun's `--frozen-lockfile` must be supplied because Bun does not enable it in CI
automatically. These are not read-only in one shared sense: several replace the installed
tree even when they leave the lock alone.

Contrast that with a resolution change. `npm install` can update the lock when ranges
require a new resolution, `pnpm install --lockfile-only` rewrites `pnpm-lock.yaml` and
`package.json` without `node_modules` writes, and `bun update` rewrites `package.json` and
`bun.lock` within the declared ranges. The question "is the lock current" and the action
"make the lock current" are separate, and each manager spells them with different
commands and write sets.

## Diagnostic: A Successful Install And A Failing TypeScript Check

An install exit code proves that the manager built a tree for the recorded lock and
configuration; it does not prove that the declarations the compiler reads match the
runtime the project targets. A common shape is a project whose active `node` executable is
a newer major version while its installed declaration package for Node, such as
`@types/node`, is still resolved at an older major through a workspace range or a hoisted
copy. The install succeeds, and the TypeScript check then fails on APIs the older
declarations do not describe. The opposite mismatch can let a check pass while the runtime
lacks the API, which is a runtime question rather than evidence about the install.

Diagnose the pair, not the exit code. Record the active runtime version, the installed
declaration package version and path, whether that path is package-local or hoisted, and
the compiler's effective program. Then route the finding: program membership and target
sets belong to `node-quality-workflow -> reference/quality-scope-and-mutation.md`,
declaration output and consumer resolution belong to
`node-package-distribution -> reference/consumer-resolution-and-declarations.md`, and
runtime and module mechanics belong to
`node-project-reference -> reference/runtime-and-project-structure.md`. An install
success is not evidence about either version.

## Limits And Qualifications

- **Version-scoped, not equivalent.** Every manager claim is tied to the publisher page
  and version or page generation named with it. No claim here is a default, a
  recommendation, a compatibility conclusion, or a tested cross-tool comparison, and no
  install, update, lock conversion, or lifecycle probe was run to produce this page.
- **Publisher currency differs.** npm is pinned to CLI v12; pnpm is mostly unversioned with
  feature annotations such as v12.7.0; Yarn Modern is unversioned while Classic identifies
  Yarn 1; Bun is rolling and names versions only for particular changes. A statement is
  the publisher's documented mechanism for that page, not a guarantee for another
  installed version.
- **Manager capability is not runtime evidence.** Bun's documented ability to install
  dependencies in existing Node.js projects establishes manager capability only. It does
  not establish that the application executes under Bun, that Node tooling was replaced,
  or that the resolved graph is the one a Node process loads.
- **Labels do not fix a write set.** Frozen, immutable, CI, and production mean different
  things per manager and command, and a lock-currency check can still replace an installed
  tree. Read the named command's effect instead of inferring from the label.
- **Documentation can conflict or lag.** The npm v12 and Bun shrinkwrap wording and the
  lockfile-version statements remain visibly unresolved here. Published pages also do not
  prove the manager, runtime, platform, resolved graph, or command used by a specific
  project.
- **No policy is established.** This page sets no organization-wide security, license,
  migration, or manager-selection policy, and it does not promise that two managers behave
  the same for a shared manifest field.

## Ownership And Routes

Manager-specific semantics in this page belong to the `node-project-dependencies`
operation. Candidate evaluation, the no-add, add, replace, and defer decision, and
authorized install, lock, workspace, and environment changes belong to
[Evaluation And Environment Changes](evaluation-and-environment-changes.md). The shared
reference interprets manager, workspace, lockfile, layout, and invocation clues but does
not reproduce these mechanics:
`node-project-reference -> reference/manager-workspaces-and-invocation.md`.

- Runtime execution, TypeScript checking, module resolution, and the canonical mixed
  manager-and-runtime case: `node-project-reference -> reference/runtime-and-project-structure.md`.
- Check scope, target sets, and a changed file missing from a green check:
  `node-quality-workflow -> reference/quality-scope-and-mutation.md`.
- Production behavior changes that must respect the recorded runtime, manager, and
  invocation: `node-project-writer -> reference/change-design-and-validation.md`.
- Package artifacts, declaration output, and consumer resolution:
  `node-package-distribution -> reference/consumer-resolution-and-declarations.md`.
- Project structure and outcome planning around workspaces:
  `node-domain-planning -> reference/project-structure.md`.
- This repository's deterministic utilities under `scripts/node/` keep their separate
  route through `skill-script-node-writer` and `skill-script-node-test-writer`; their Bun
  and repository conventions are not evidence about an application's manager.

When an observation cannot be tied to a manager version and a command, report that gap. A
declaration is not a substitute for the installed state, the lock is not a substitute for
the executable, and the correct answer is often narrower than the requested one.
