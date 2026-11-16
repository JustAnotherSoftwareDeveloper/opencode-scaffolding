# Evaluation And Environment Changes

## Purpose

Describe the dependency and environment distinctions that inform a bounded project
decision. This reference is not a manager recommendation, migration policy, security
standard, or compatibility guarantee. It owns the dependency and environment decision and
authorization question for Node.js or Bun projects whose TypeScript source,
configuration, declarations, tests, quality diagnostics, and package artifacts are the
subject; documented manager mechanics belong to
[Manager Semantics And Workspace Placement](manager-semantics-and-workspace-placement.md).
Standalone JavaScript guidance and the `allowJs`, `checkJs`, and JSDoc typing options for
`.js` files are outside this reference, and a JavaScript-only request is out of scope.

## Evaluate A Dependency

Tie the candidate to a concrete capability the project needs. Compare it with existing
code and already-approved dependencies before proposing another package. Check the
candidate's documented API and package identity, target versions and platforms, runtime
requirements, dependency roles, install/build implications, maintenance evidence, and
known security or license information that is relevant and available. Record source,
access/version context, and limitations. Documentation, metadata, and automated
indicators are evidence inputs, not proof that the candidate works in the target project.

Distinguish a dependency finding from an authorization or policy decision. A security
advisory, license field, popularity measure, or scan result does not alone decide whether
to adopt or reject a package. Escalate unresolved legal, organizational, or risk-policy
questions to their responsible owner; this workflow establishes no organization-wide
security policy or legal conclusion.

### Record The Candidate Before Deciding

Record these six items before the decision, because each one carries its own evidence
class and its own scope:

- **Exact package and version.** `name@version`, not a floating tag, plus the expected
  registry and the scope or owner that name should route to.
- **Required API.** The exports, subpath, type surface, or command the need depends on,
  and what the project would call if the candidate were absent.
- **Declared runtime and platform range.** The Node.js or Bun version and the operating
  system or architecture conditions the publisher states, with the page that states
  them.
- **Install path.** Registry tarball, workspace member, Git source, or local path, and
  the manager and version that would fetch or build it.
- **Maintenance evidence.** Release history and support statements for that version, and
  any security or license information that is available.
- **Authorized project check.** The exact check, target runtime version, platform, and
  configuration that would test the need, when such a check is authorized.

Popularity, download counts, badges, scans, and metadata narrow that investigation; none
of them decides adoption.

### Choose No-Add, Add, Replace, Or Defer

The decision is one of four outcomes, and each states the evidence class it rests on.
Publisher metadata reports what the publisher claims; install-path evidence is what the
selected manager would fetch, build, or link; authorized project evidence is what a check
actually exercised on the target runtime, version, platform, and configuration. A
conclusion drawn only from the first two is a documentation-level conclusion, not a
compatibility result.

- **No-add.** Existing project code, a standard-library surface, or an already-approved
  dependency covers the need. Name the capability that covers it. Adding a package anyway
  moves an existing responsibility and changes the resolved graph for no evidenced gain.
- **Add.** A concrete need and the evidence above support the candidate within known
  constraints. State the group the package joins, the manager and version that define
  that group, and the install path; the group is a role decision, not a formality.
- **Replace.** An evidenced shortfall or defect in the current package, together with an
  understood migration impact, justifies the change, including the lockfile, declaration,
  and consumer effects of running two versions during the transition.
- **Defer.** A candidate whose needed API is present but whose target-runtime claim and
  native or optional install path are unchecked gets a defer result, never "supported"
  and never "incompatible". When the only evidence is publisher metadata, the result is
  also defer, with the missing check named. A defer names the smallest next authorized
  check or the owner decision that would resolve it; it does not install speculatively
  unless that effect is authorized.

## Keep Project Layers Distinct

- **Runtime:** executes project code. Node.js and Bun are distinct runtimes; project
  compatibility must be grounded in the actual target and version evidence.
- **Package manager:** interprets dependency declarations and performs resolution or
  installation. Bun can manage packages for a Node.js project, so a Bun install command
  does not establish Bun runtime execution. How a named manager and version documents
  groups, peers, workspaces, locks, and install commands is stated in
  [Manager Semantics And Workspace Placement](manager-semantics-and-workspace-placement.md).
- **Lockfile:** records manager-specific resolution state. Lock formats and install
  semantics are not a common cross-manager contract. Importing or converting a lockfile
  does not prove complete semantic equivalence or safe concurrent writes by multiple
  managers. Bun documents the text `bun.lock` as its default lockfile since v1.2, which is
  a versioned Bun statement rather than a format rule for other managers
  ([Bun lockfile](https://bun.com/docs/pm/lockfile)).
- **Workspace:** describes package membership and local relationships. Membership,
  linking layout, task graphs, lockfile scope, and filtering differ by manager and
  version. Inspect the relevant workspace root and target package rather than assuming
  repository root is the only package boundary; "Place A Dependency In A Workspace" below
  works one placement question through those layers.
- **Environment selection:** compatibility declarations, package-manager dispatch,
  runtime pinning, and the executable actually invoked are separate mechanisms. Fields
  such as `engines` or `packageManager` do not have one universal enforcement effect; the
  active tool and configuration matter. Which source supplied a value is also
  loader-specific and version-bounded: an inherited process value wins over a file, Node's
  and Bun's `--env-file` options give a later file priority while a dotenv-family API
  keeps the first file's value by default, Bun chooses automatic mode files with `BUN_ENV`
  before `NODE_ENV` according to the pinned Bun 1.3.14 loader, and parsed values are
  strings, so presence and validated meaning are separate facts
  ([Node.js v26.13.1 CLI](https://nodejs.org/download/release/v26.13.1/docs/api/cli.html);
  [Bun environment variables](https://bun.com/docs/runtime/environment-variables);
  [Bun environment loader at `bun-v1.3.14`](https://github.com/oven-sh/bun/blob/bun-v1.3.14/src/dotenv/env_loader.zig);
  [dotenv v18.0.9](https://github.com/motdotla/dotenv/tree/v18.0.9)). Per-loader
  precedence, mode selection, and validation are resolved in
  `node-project-reference -> reference/configuration-loading-and-validation.md`.

## Decide A Package's Role

Start from who imports or provides the package and when it is needed, then read the
selected manager's group, peer, and optional semantics for the manager and version in
use. The dependency field records who installs the package for a consumer; it does not
prove that the package executes, and a `devDependencies` entry does not prove that a
package is unused in production compilation.

Three role situations cover most candidates:

- **Build-time tool.** A compiler, bundler, or checker used only to type-check or emit
  during development or CI belongs to the development group, which npm documents as not
  being installed for a consumer of the package
  ([package.json, npm CLI v12](https://docs.npmjs.com/cli/v12/configuring-npm/package-json/)).
  `typescript` is this case when only `tsc` runs; a transpiler-only setup that does not
  type-check may run no separate compiler at all.
- **Published runtime code.** Code that imports the compiler API — for example
  `import * as ts from "typescript"`, `ts.createProgram(...)`, and `program.emit()` — uses
  the package as a runtime, or at least a production, dependency for that path.
- **Downstream typing graph.** When a package's emitted declarations expose types from
  another package, that declaration package belongs in `dependencies`, because consumers'
  compilation needs it too. TypeScript's publishing guidance addresses declaration
  dependencies whose types leak into published signatures; it is not a rule that every
  package must depend on its own `@types`
  ([Publishing, TypeScript](https://www.typescriptlang.org/docs/handbook/declaration-files/publishing.html)).

A package that emits and ships its own declarations needs no external declaration
package for its own types. A declaration-only package such as `@types/node` contributes
compile-time types rather than runtime code, so its role is set by the field its author
chooses and the tool that reads that field.

Manager group, peer, and optional semantics then bound where the package is installed:

- **npm CLI v12.** Peers are installed by default; an optional peer marked in
  `peerDependenciesMeta` is not installed automatically; an optional dependency's install
  failure need not fail the install, so consuming code must handle its absence.
- **pnpm v12.x.** `autoInstallPeers` is documented as enabled by default, while an
  optional peer that is missing is not installed and resolves to an already-installed
  version that satisfies the optional range when one is available. `addMissingPeerTypes`,
  added in v12.12.0 and defaulting to `false`, makes the matching `@types` package an
  optional peer and links it beside the package that peer-depends on the library
  ([peer dependency settings, pnpm](https://pnpm.io/settings/peer-dependencies)).
- **Yarn Modern (`v6` documentation site).** `devDependencies` are required when the
  package is installed as part of a workspace, and a peer dependency gives the package the
  same instance as its ancestor; Yarn Classic 1.x is a separate generation with its own
  semantics ([manifest, Yarn](https://yarnpkg.com/configuration/manifest)).
- **Bun (rolling pages).** `bun install` installs `dependencies`, `devDependencies`, and
  `optionalDependencies` and installs peers by default; `--omit` selects groups, and
  `trustedDependencies` decides which dependency lifecycle scripts run
  ([bun install](https://bun.com/docs/pm/cli/install)).

Two compiler options that shape a declaration package's reach are also distinct. `types`
filters which packages contribute global scope during compilation, and it does not affect
how `@types/*` are included in application code, so `types: []` does not disable resolving
declarations for an imported package; since TypeScript 6.0 the `types` default is `[]`, and
`"types": ["*"]` restores the earlier all-visible behavior
([`types`, TSConfig](https://www.typescriptlang.org/tsconfig/types.html);
[TypeScript 6.0](https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/)).
`typeRoots` is a different option: since TypeScript 5.1 it participates as a
module-resolution fallback when the normal lookup fails, and an explicit `typeRoots`
disables the upward walk through parent `node_modules/@types` folders, which can surface
`TS2688: Cannot find type definition file`; earlier compilers keep the prior lookup
behavior ([`typeRoots`, TSConfig](https://www.typescriptlang.org/tsconfig/typeRoots.html);
[TypeScript 5.1](https://devblogs.microsoft.com/typescript/announcing-typescript-5-1/)).

No manager-neutral rule fixes a declaration-only package's role. Version alignment is a
publishing convention, not a compatibility guarantee: DefinitelyTyped publishes a
`major.minor.x` value whose major and minor follow the library while the patch increments
independently, and declaration updates commonly lag the library
([DefinitelyTyped](https://github.com/DefinitelyTyped/DefinitelyTyped)).

## Place A Dependency In A Workspace

A dependency edge belongs to the package that imports the API. The root workspace
declaration decides membership; it does not decide where the edge goes.

Consider a repository whose root manifest declares `"workspaces": ["packages/*"]`, with an
`@repo/api` package and an `@repo/cli` package, and take npm CLI v12 as the selected
manager. Only `@repo/api` imports the new runtime dependency:

```json
{
  "name": "@repo/api",
  "dependencies": { "zod": "^4.0.0" }
}
```

The target package is `@repo/api`; the workspace root is the directory whose manifest
holds the `workspaces` globs; the declaration belongs in `@repo/api`'s own `dependencies`;
and the lockfile boundary is the root lock the selected manager writes for that workspace.
For npm CLI v12, that is the root `package-lock.json`, produced by an install that
symlinks each matched workspace package into the root `node_modules`
([npm workspaces](https://docs.npmjs.com/cli/v12/using-npm/workspaces/)).

Whether `zod` resolves from the registry or from a local member is a separate question,
and a version range alone does not answer it. pnpm documents `workspace:` requiring
resolution to a local workspace package, Modern Yarn documents `workspace:` references
with publish-range rewriting, and Bun documents `workspace:` references
([pnpm workspaces](https://pnpm.io/workspaces);
[Bun workspaces](https://bun.com/docs/pm/workspaces)). Check the declared protocol or
range, the manager and version, and the importer entry for `@repo/api` in that manager's
lockfile before calling the dependency local or remote.

Adding the package to every member to make one package's command resolve hides the
placement question and changes every member's manifest. Use the manager's selection
option to run the install or check for the one package, and work the two placement
questions through manager-specific evidence in
[Manager Semantics And Workspace Placement](manager-semantics-and-workspace-placement.md#two-candidate-questions).

## Check Package Identity

Package identity is a set of dimensions, each verified at its own layer, not a single
name comparison. A familiar-looking name is not a check, and a record that cannot
attribute a publisher is a stated limitation of that record rather than an unknown
identity.

1. **Fix the exact candidate.** Record `name@version`, the expected registry, and the
   scope or owner that name should route to. A scoped package's scope is the namespace
   between `@` and the slash, and npm administers scopes to users and organizations
   ([npm scopes](https://docs.npmjs.com/about-scopes)).
2. **Read the registry record for that version.** Run `npm view` for the exact
   `name@version` spec and read its `dist.integrity`, `dist.shasum`, `dist.tarball`, and
   `dist.signatures` fields, which report the configured registry's metadata for that
   version. When an alias or a non-registry locator is in play, the lockfile `resolved`
   field and the alias specifier record where the artifact actually comes from
   ([npm view](https://docs.npmjs.com/cli/v12/commands/npm-view/)).
3. **Compare digests at the correct layer.** Registry `dist.integrity` and the lockfile's
   `integrity` or `resolution.integrity` are metadata that should agree. Do not compare an
   extracted `node_modules` tree against a tarball digest: extraction, symlinks, and build
   transforms change bytes. To check download bytes, compare the tarball or the manager
   cache entry digest against the recorded value
   ([package-lock.json, npm CLI v12](https://docs.npmjs.com/cli/v12/configuring-npm/package-lock-json/);
   [pnpm lockfile](https://pnpm.io/lockfile)).
4. **Verify signatures and provenance with a versioned client.** Registry signatures are
   ECDSA and cover registry-served tarballs; PGP signatures were deprecated and removed in
   2023 ([registry signatures, npm](https://docs.npmjs.com/about-registry-signatures)).
   `npm audit signatures` verifies registry signatures from npm v8.15.0 and provenance
   attestations from v9.5.0, after dependencies are installed with `npm install` or
   `npm ci`. Its documented error cases are a missing signature while the registry
   provides signing keys, and an invalid signature or attestation
   ([npm audit](https://docs.npmjs.com/cli/v12/commands/npm-audit/)). Provenance is a
   separate layer that records a build and source context in a public transparency
   ledger, and absent provenance is normal rather than an error
   ([provenance, npm](https://docs.npmjs.com/generating-provenance-statements)).
5. **Establish expected-owner evidence separately.** A matching digest, a valid signature,
   and a valid attestation establish registry binding and, for provenance, a build
   context. None of them proves that the expected party published the code. `repository`
   and `maintainers` are publisher-supplied fields, not independent trust anchors, so
   compare scope ownership, the known upstream project, and the expected release process
   as separate evidence.

These bounds travel with the record: consistency is not authenticity, signatures and
provenance depend on the registry, client, and CI provider, and git, local-path, and
arbitrary tarball dependencies fall outside registry signature coverage. `npm view` reads
whatever registry is configured, so an alternative registry or mirror can return
different metadata, and the npm registry metadata page is stale about the legacy
`npm-signature` field even though its integrity and tarball fields remain current.
Archive-level inspection and consumer verification remain with
`node-package-distribution -> reference/artifact-and-consumer-boundaries.md`, and
declaration resolution with
`node-package-distribution -> reference/consumer-resolution-and-declarations.md`.

## Reconcile Mixed Manager And Runtime Clues

Suppose a repository contains `bun.lock`, while one package declares:

```json
{
  "scripts": { "start": "node server.js" }
}
```

These clues answer different questions. The lockfile is evidence of Bun package-manager
state; it does not show that Bun runs the application. The manifest text declares a
script command, but does not prove that this script was invoked in a particular run.
Inspect the package boundary, the command recorded by CI or the request, and the actual
launcher before stating which runtime ran. Bun documents `bun run` as respecting a
`#!/usr/bin/env node` shebang by default and `bun run --bun` as overriding it; these are
Bun launcher behaviors, not an inference about an unseen invocation. See [Bun runtime
documentation](https://bun.com/docs/runtime) and [Bun package-manager use in
Node projects](https://bun.com/docs/pm/cli/install).

Module mode is another question: for Node, inspect the nearest package `type` field and
the file extension (`.mjs`/`.cjs` are explicit signals); do not derive it from the
lockfile. These are the clearest indicators, not an exhaustive decision rule. The Node.js
Packages page that identifies itself as v26.13.1 documents syntax detection for ambiguous
`.js` input without an explicit marker: ESM-only syntax may cause the file to be
interpreted as ESM, and the feature is marked Stability 1.2 (Release candidate). See
[Node's module-system determination](https://nodejs.org/api/packages.html#determining-module-system).
Check the target Node version and the actual invocation before concluding module mode. The
full worked case, including module mode and the ambiguous `.js` file, is the canonical
mixed-clue case in
`node-project-reference -> reference/runtime-and-project-structure.md#reconcile-mixed-runtime-clues`;
it is not restated here.

### Keep The npm v12 And Bun Lockfile Wording Visible

npm CLI v12's lockfile page states that npm no longer reads or writes
`npm-shrinkwrap.json`, including a dependency-tarball shrinkwrap
([package-lock.json, npm CLI v12](https://docs.npmjs.com/cli/v12/configuring-npm/package-lock-json/)).
Bun's lockfile page states that Bun migrates that file, prefers it over
`package-lock.json` when both are present, and does so "as npm does"
([Bun lockfile](https://bun.com/docs/pm/lockfile)). The same pages disagree in shape: npm
v12 lists lockfile versions 1, 2, and 3, its `.npm-extension` page requires
`lockfileVersion: 4` for extension state, and Bun's importer lists versions 2, 3, and 4.
The inspected pages do not reconcile that difference, and this page does not decide which
source is stale. Record the npm version, the lockfile name, the `lockfileVersion` field,
and the command that reads the file; treat the version as a value to qualify rather than a
cross-tool compatibility promise, and do not delete, regenerate, or edit either lockfile
to settle the disagreement. The manager-by-manager statement of install and lock effects
is in
[Manager Semantics And Workspace Placement](manager-semantics-and-workspace-placement.md#the-npm-v12-and-bun-lockfile-wording-conflict).

## Interpret Claims Without Overreading Them

Consider a hypothetical candidate with metadata like this:

```json
{
  "engines": { "node": ">=20" },
  "optionalDependencies": { "native-addon": "^2.0.0" },
  "scripts": { "install": "node install-check.js" }
}
```

This is an illustration of declarations, not a real package or compatibility finding. For
npm CLI v12, `engines` on a dependency is advisory unless `engine-strict` is enabled; an
optional dependency's install failure need not fail installation, so the consuming code
must handle its absence. The metadata does not prove that the candidate's API works on
Node 20, that Bun runs the install script, or that the optional native path is available
on the target platform. Consult npm's [package metadata
documentation](https://docs.npmjs.com/cli/v12/configuring-npm/package-json/) and the
[`engine-strict` configuration](https://docs.npmjs.com/cli/v12/using-npm/config#engine-strict)
for those npm-specific semantics. Bun's rolling
[install documentation](https://bun.com/docs/pm/cli/install) describes its own
lifecycle-script trust behavior and peer installation; do not transfer npm's behavior to
Bun or infer that either manager produces equivalent installed state.

For a real candidate, record the exact package/version and target, then distinguish:

- **Documented claim:** package documentation or metadata states a version/API/platform
  range. This identifies what to investigate, not independently verified support.
- **Install-path evidence:** inspect the actual dependency form (registry artifact,
  workspace, or Git source), selected manager/version, optional/native dependencies, and
  scripts. npm documents that some Git dependencies with build/prepare/install scripts may
  be cloned, built, packed, and installed; that statement is specific to npm's documented
  path, not all managers or registry tarballs. See [npm Git dependency
  behavior](https://docs.npmjs.com/cli/v12/configuring-npm/package-json/#git-urls-as-dependencies).
- **Project evidence:** only an authorized check under the intended runtime, package
  version, platform, and configuration can establish what that check exercised. A
  successful install is not an API/runtime test; a successful check on one platform does
  not establish another.

When these three kinds disagree — the API looks suitable, the declared runtime range is
silent or unverified, and no authorized check has run — the outcome is the defer result
described under "Choose No-Add, Add, Replace, Or Defer", not an incompatibility finding.

## Bound Environment Effects

Treat evaluation as read-only unless an explicit request authorizes a concrete effect.
Before each mutation, identify the exact project/package, manifest and lockfile, manager
and version, runtime target, install groups, platform, and files or environment that may
change. If a required selector, candidate, policy decision, or effect is unclear, ask or
defer that effect. Keep manager migration, runtime migration, package installation,
lockfile generation, and environment synchronization as distinct changes; authorization
for one does not imply authorization for the others.

Classify the requested effect before proposing it, because the labels do not describe one
shared write set:

- a read-only lock-currentness or resolution check that must not rewrite the manifest or
  lock, though it may still replace the installed tree — `npm ci` requires a matching lock,
  fails rather than updating it, and removes an existing `node_modules`
  ([npm ci](https://docs.npmjs.com/cli/v12/commands/npm-ci/));
- a resolution or update that rewrites the lock and possibly the manifest — `npm install`
  when the declared ranges require a new resolution
  ([npm install](https://docs.npmjs.com/cli/v12/commands/npm-install/)), or `bun update`
  within the declared ranges ([bun update](https://bun.com/docs/pm/cli/update));
- an install or sync that creates or removes an installed tree, links workspace packages,
  or writes cache and `.bin` entries;
- lifecycle scripts that run during an install, subject to the manager's policy such as
  Bun's `trustedDependencies` allowlist;
- an environment synchronization or selector change that edits `.env` files, a manager or
  runtime selector, or a launcher configuration without touching the lock or the installed
  tree;
- a removal that changes the manifest and, through it, the resolved graph and the
  installed tree.

Authorization for one of these is not authorization for the others. After an authorized
change, inspect the resulting diff and state. Report what the manager actually changed,
the exact check or install command and target, versions when known, and any scripts or
lifecycle effects relevant to the result. A lock-currentness check, successful
installation, type check, or static compatibility declaration proves only its stated
scope; it does not establish application behavior or compatibility with an untested
runtime, package, platform, or artifact consumer.

## Examples

### A Declaration Package In A Development Group

A library that checks its own sources against the Node target records the declaration
package in `devDependencies`:

```json
{
  "name": "@repo/api",
  "devDependencies": { "@types/node": "^24.0.0" }
}
```

The package is consumed by this project's compiler and test run, and npm documents that a
consumer installing `@repo/api` does not receive it
([package.json, npm CLI v12](https://docs.npmjs.com/cli/v12/configuring-npm/package-json/)).
It does not ship in the built artifact unless the project moves it. If the emitted
declarations expose Node types to consumers, the role changes and the declaration package
becomes a `dependencies` entry, as in the downstream typing graph case.

### A Runtime Dependency That Exports Types

A package that ships its own declarations and is imported at run time belongs in
`dependencies` for the consumer: the compile and the execution both need it, and no
separate `@types` package plays that role. The distinction that matters is who needs the
package and when, not which field name looks type-related. A bundled-declaration package
needs no external declaration package for its own types, while a package whose
declarations leak a third-party type pulls that third-party declaration package into
`dependencies`.

### A Declaration Package Pinned To The Node Target

A workspace on Node 24 with `@types/node@^22` in its development group compiles against
declarations for an older major. Whether a declaration package must match the runtime
major is a question to verify against the publisher's statement before asserting it:
`@types/node` versions follow the Node major/minor, and a matching major/minor does not
prove type or API compatibility. Record the active runtime version, the resolved
declaration version and path, whether that path is package-local or hoisted, and the
compiler's effective program. A check can then reject APIs the newer runtime provides,
while the reverse mismatch can pass the check and fail at run time. Declaration
resolution details belong to
`node-package-distribution -> reference/consumer-resolution-and-declarations.md`.

### Defer When The Evidence Is Publisher Metadata

A candidate documents the needed API, declares `"engines": { "node": ">=20" }`, and ships
an optional native addon. The project's Node version and platform are known, but no
authorized check has run and the publisher states nothing about that platform. The result
is defer: name the missing target-runtime and native install-path evidence and the
smallest authorized check that would produce it. The candidate is not "supported", because
no project evidence exists, and not "incompatible", because nothing shows failure.

### A Workspace Protocol Range

A workspace manifest records `"@repo/tooling": "workspace:*"`. The meaning of that range
must be checked for the selected manager and version: npm documents symlinking matched
workspace packages during an install, pnpm documents `workspace:` requiring resolution to
a local workspace package, and Modern Yarn documents `workspace:` references with
publish-range rewriting
([npm workspaces](https://docs.npmjs.com/cli/v12/using-npm/workspaces/);
[pnpm workspaces](https://pnpm.io/workspaces);
[Yarn workspaces](https://yarnpkg.com/features/workspaces)). A plain version range can also
link locally under some managers, so read the declared protocol or range, the manager and
version, and the lockfile importer entry for the consuming package before calling the
dependency local or remote.

## Diagnostic: A Plausible Declaration Is Not Support

A plausible declaration is insufficient, so a deferred candidate is never reported as
supported or as incompatible. A manifest can name the expected version range, a
`types` entry can point at declarations, and an install can exit zero while the needed API
is absent at the target runtime or platform. A typical shape is an optional native
dependency that does not build on the target platform: the install succeeds without the
addon and the import fails later, which is a runtime and platform result rather than an
install failure.

Report the unchecked dimension, the evidence class that is missing, and the exact check
that would close it, instead of converting a gap into a verdict. An install success is not
an API test, a green check on one platform is not another platform, and an integrity match
is not an authenticity finding.

## Limits And Qualifications

- **Manager examples are scoped snapshots.** Every manager statement stays with the
  publisher page and version or page generation named beside it. None is a default, a
  recommendation, or a tested cross-tool comparison, and the representative manager
  mechanics are documented in one place,
  [Manager Semantics And Workspace Placement](manager-semantics-and-workspace-placement.md).
- **Metadata does not prove behavior.** Publisher declarations and registry records do not
  prove runtime support, install behavior, or platform availability in the target project.
- **Consistency is not authenticity.** A matching digest, a valid signature, or a valid
  provenance attestation establishes registry binding and, for provenance, a build
  context; it does not establish who published the code or that the code is safe.
- **Environment selection is loader-specific.** The inherited-versus-file and
  file-versus-file orderings, Bun's mode selector, and string-valued parsing are bounded
  to the pages and versions named above, and third-party loaders are separate products
  rather than aliases for the built-ins.
- **Role follows field plus tool.** No manager-neutral rule fixes a declaration-only
  package's role, and a matching major/minor is a publishing convention rather than a
  compatibility guarantee.
- **No policy is established.** This page sets no organization-wide security, license,
  migration, or manager-selection policy; unresolved legal, organizational, or risk
  questions go to their responsible owner.
- **No effect was exercised here.** The examples are illustrative and the commands are
  quoted, not run; no install, update, lock conversion, or lifecycle probe produced this
  page.

## Ownership And Routes

Dependency and environment decisions, and the authorization for any resulting effect,
belong to the `node-project-dependencies` operation. A recommendation is not
authorization, and every manifest, lockfile, install, workspace, or environment change
requires an explicit requester authorization that names the target and the effect.

- Manager groups, peers, optional dependencies, workspaces, locks, install commands, and
  the preflight for a requested install or lock change:
  [Manager Semantics And Workspace Placement](manager-semantics-and-workspace-placement.md).
- Runtime execution, TypeScript processing, module resolution, and the canonical mixed
  manager-and-runtime case:
  `node-project-reference -> reference/runtime-and-project-structure.md#reconcile-mixed-runtime-clues`.
- Manager, workspace, lockfile, layout, and invocation evidence layers:
  `node-project-reference -> reference/manager-workspaces-and-invocation.md`.
- Environment loading precedence, mode selection, and validation:
  `node-project-reference -> reference/configuration-loading-and-validation.md`.
- Production behavior changes that must respect the recorded runtime, manager, and
  invocation: `node-project-writer -> reference/change-design-and-validation.md`.
- Tests and coverage for an existing contract:
  `node-project-test-writer -> reference/test-design-and-measurement.md`.
- Standalone quality configuration and diagnostics:
  `node-quality-workflow -> reference/quality-scope-and-mutation.md`.
- Package artifacts, archive and consumer verification, and declaration resolution:
  `node-package-distribution -> reference/artifact-and-consumer-boundaries.md` and
  `node-package-distribution -> reference/consumer-resolution-and-declarations.md`.
- Project structure and outcome planning around workspaces:
  `node-domain-planning -> reference/project-structure.md`.
- This repository's `scripts/node/` utilities keep their separate route through
  `skill-script-node-writer` and `skill-script-node-test-writer`; their Bun and repository
  conventions are not evidence about an application's manager.

When an observation cannot be tied to a manager, runtime, version, and command, report
that gap. A declaration is not a substitute for the installed state, the lock is not a
substitute for the executable, and the correct answer is often narrower than the
requested one.
