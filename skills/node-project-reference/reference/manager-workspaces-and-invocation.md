# Manager, Workspace, And Invocation Evidence

## Scope

This page answers which package manager and version, lockfile, workspace root, target package, install layout, working directory, wrapper, and executable a project observation concerns, and what each of those artifacts does and does not establish. It interprets evidence for TypeScript work in Node.js or Bun projects. It does not state how a particular manager implements dependency groups, peers, workspace linking, lock writes, or lifecycle scripts, and it does not evaluate a candidate package, choose a manager, or authorize an install, lock, or workspace change.

The layers are ordered for a reason: a manifest constrains a lockfile, a lockfile constrains an install, an install produces a layout, a layout determines which binaries a script can reach, a script is started by a wrapper, and a wrapper starts an executable. Each layer records something real, and none of them proves the next. Most misreadings of a project come from collapsing two layers, such as treating a lockfile as proof of the executing runtime or a script line as proof of the command that ran.

Manager-specific mechanics belong to `node-project-dependencies -> reference/manager-semantics-and-workspace-placement.md`; candidate evaluation and authorized install, lock, or workspace work belong to `node-project-dependencies -> reference/evaluation-and-environment-changes.md`. Runtime execution, checking, module resolution, and the worked manager-and-runtime clue case are covered in [Runtime And Project Structure](runtime-and-project-structure.md).

Statements about a manager stay with the publisher, version, command, and configuration they describe. npm documentation is version-pinned to CLI v12; pnpm documentation is mostly unversioned with feature-specific annotations; Yarn Modern pages are unversioned while Yarn Classic pages identify Yarn 1; Bun package-manager pages are rolling and name versions only for particular changes. No install or invocation experiment supports this page, so it describes documented mechanisms and how to read project evidence, not a tested cross-manager baseline.

The subject is TypeScript source, configuration, declarations, tests, quality diagnostics, and package artifacts. Standalone JavaScript source guidance, JavaScript checking through `allowJs` and `checkJs`, and JSDoc typing of `.js` files are outside this reference; a JavaScript-only request is out of scope.

## Seven Layers Of Evidence

Read an observation against these layers before drawing a conclusion. The list is ordered from declaration to process, and the boundary between each pair is where evidence stops.

- **Manifest.** The `package.json` nearest the work declares the package name, dependency ranges, `scripts` entries, `type` field, and, in a workspace root, the member globs. npm's package.json page defines those fields and the dependency-group roles ([package.json, npm CLI v12](https://docs.npmjs.com/cli/v12/configuring-npm/package-json/)). A manifest establishes declared intent. It does not establish a resolved version, an installed tree, the manager that will act on it, or the script that ran. Two packages can declare the same `typescript` range and resolve different compilers, and a script entry is text until a manager executes it.

- **Lockfile.** A lockfile is the selected manager's resolution record: `package-lock.json` for npm, `pnpm-lock.yaml` for pnpm, `yarn.lock` for Yarn, or `bun.lock` for Bun. npm describes its lock as the exact tree and the input `npm install` compares against ([package-lock.json, npm CLI v12](https://docs.npmjs.com/cli/v12/configuring-npm/package-lock-json/)); pnpm documents importer, package, and snapshot records ([pnpm lockfile](https://pnpm.io/lockfile)); Yarn Modern distinguishes lockfile immutability from cache immutability ([yarn install](https://yarnpkg.com/cli/install)); Yarn Classic treats a sufficient `yarn.lock` as the exact-version install input ([yarn install, Yarn Classic](https://classic.yarnpkg.com/en/docs/cli/install/)); Bun made the text `bun.lock` the default in v1.2 ([Bun lockfile](https://bun.com/docs/pm/lockfile)). A lockfile establishes which resolutions one manager recorded under one format version and which commands may reuse or rewrite them. It does not establish the executing runtime, that the installed tree matches it, or that the invoked manager is the one that reads it. Read the lockfile version and manager version before reasoning from it.

- **Workspace membership.** Membership is the manager's declaration of which directories are linked local packages. npm, Yarn, and Bun read root `workspaces` globs; npm documents auto-symlinking each matched package into the root `node_modules` during install ([npm workspaces, CLI v12](https://docs.npmjs.com/cli/v12/using-npm/workspaces/)). pnpm ordinarily reads a `pnpm-workspace.yaml`, and its conversion of a root manifest workspace list is annotated as added in pnpm v12.7.0 ([pnpm workspaces](https://pnpm.io/workspaces)). Yarn Modern documents `workspace:` references and publish-range rewriting ([Yarn workspaces](https://yarnpkg.com/features/workspaces)), while Yarn Classic documents one shared workspace lockfile ([Yarn Classic workspaces](https://classic.yarnpkg.com/en/docs/workspaces/)). Bun documents negative globs, workspace filtering, and workspace directories outside the root ([Bun workspaces](https://bun.com/docs/pm/workspaces)). Membership establishes which packages that manager may treat as workspace members for linking, filtering, and installation. It does not establish equivalent membership under another manager, that a dependency range resolves to the local member rather than the registry, that every member declares a script, or that a root command spans every member.

- **Install layout.** Layout is what an install or link step placed on disk: directories, symlinks, hoisted or isolated placements, and `.bin` entries. npm shows the workspace symlink it creates (`node_modules/a -> ../packages/a`) ([npm workspaces](https://docs.npmjs.com/cli/v12/using-npm/workspaces/)). Bun's install page documents install strategies and linker defaults, and its workspaces page documents de-duplicating installs across a workspace ([Bun install](https://bun.com/docs/pm/cli/install); [Bun workspaces](https://bun.com/docs/pm/workspaces)). Layout establishes which local package instances and binaries a command can reach from a given directory. It does not establish which declaration produced them, whether the tree is current, or which runtime will load them. A script that finds `tsc` through `node_modules/.bin` has demonstrated reachability, not a manifest edge; a package-local `devDependencies` entry can be satisfied by a hoisted copy or by a nested one.

- **Script declaration.** A `scripts` entry names a command string inside one package. npm documents that `npm run` starts the named script from the root of that package folder regardless of the caller's working directory, adds `node_modules/.bin` to the script's `PATH`, sets `NODE` to the `node` executable that runs npm, and exposes the caller's directory as `INIT_CWD` ([npm run, CLI v12](https://docs.npmjs.com/cli/v12/commands/npm-run)). The declaration establishes a name and text in a package. It does not establish that the script ran, which package it ran in, which manager or shell started it, or which executable the text resolved to. A line such as `"check": "tsc -p tsconfig.json --noEmit"` says that a compiler is expected to run against the package configuration; it says nothing about the compiler version or the configuration actually read.

- **Wrapper.** A wrapper is the layer that looks up and starts the real program: a script that chains another script, `npm run`, `pnpm run`, `yarn run`, or `bun run`, a `node_modules/.bin` shim, `npx` or `bunx`, a Corepack shim, or a launcher supplied by a version manager. A wrapper establishes where the selection happened and which selection rule applies. It establishes the resulting executable only when that rule is pinned or the result is observed. Bun documents launcher behavior that is sensitive to shebang selection and a `--bun` override ([Bun runtime](https://bun.com/docs/runtime)), so changing the wrapper can change the runtime while the manifest and script text stay identical. A wrapper is therefore not a neutral transport.

- **Executable actually started.** The executable is the process that ran: its path, version, arguments, working directory, environment, and parent process. Only an invocation record establishes it. A version command run in the same shell and working directory, the tool's own version output, a process listing, or a CI log is direct evidence. No manifest, lockfile, workspace declaration, layout, or script line substitutes for it. When the executable is unrecorded, the observation remains a statement about files rather than about behavior.

## From A Root Script To A Package-Local TypeScript Command

A root script reaches a package-local TypeScript command through the root manager's workspace route. There is no shared cross-manager route, so the exact command is part of the evidence.

Consider a root manifest that owns a workspace and a script which asks npm to run a script in that workspace:

```json
{
  "name": "app-repo",
  "private": true,
  "workspaces": ["packages/web"],
  "scripts": {
    "check:web": "npm run check --workspace=web"
  }
}
```

The workspace package declares the actual compiler command:

```json
{
  "name": "web",
  "scripts": {
    "check": "tsc -p tsconfig.json --noEmit"
  },
  "devDependencies": {
    "typescript": "^6.0.0"
  }
}
```

When the user runs `npm run check:web` from the repository root, the layers interact as follows:

1. The outer npm starts the root script from the root package folder and exposes the caller's directory as `INIT_CWD`.
2. The root script starts npm again with `--workspace=web`, which selects the `web` workspace by name; npm documents this filtering form and the equivalent implicit selection when the current directory is already inside a workspace ([npm run](https://docs.npmjs.com/cli/v12/commands/npm-run); [npm workspaces](https://docs.npmjs.com/cli/v12/using-npm/workspaces/)).
3. The inner npm runs the `check` script from `packages/web`, so the script's working directory is the package folder, not the repository root.
4. The script's `PATH` includes the `node_modules/.bin` entry npm adds, so `tsc` is found through the install layout rather than by an absolute path in the script.
5. `tsconfig.json` resolves from `packages/web`, and the compiler that starts is whichever `tsc` the layout exposed at that point.

The nesting explains two working directories that are easy to confuse. The outer script starts at the root package folder, and the package script starts at the workspace folder. npm's `INIT_CWD` records where `npm run` was invoked, so a relative argument written in the root script and a relative argument written in the package script have different bases. A command copied from a shell session into a script, or from a root script into a package script, can therefore address a different file without changing any text.

The route also differs by manager, and the difference is behavioral rather than cosmetic. pnpm documents `--filter` selectors for running commands on chosen workspace packages ([pnpm filtering](https://pnpm.io/filtering)). Bun documents `bun run --filter` and `--workspaces` for running scripts across packages and applies its own workspace exclusion rules ([Bun workspaces](https://bun.com/docs/pm/workspaces)). Yarn Modern documents `yarn workspaces foreach` for running a script across workspaces and states that manifest scripts are run with `yarn run` from inside the workspace ([Yarn workspaces](https://yarnpkg.com/features/workspaces)). These routes are not interchangeable spellings: they select packages differently, run in different directories, and honor different configuration. Record the exact command the root script contains instead of translating it into another manager's form.

A root script can bypass the package script entirely, for example with `tsc -p packages/web --noEmit`. That invocation starts the compiler in the root package, resolves the project path from the root, and reaches a binary through the root layout. It may check the same files, but it is different evidence: the package's own script and `INIT_CWD` are no longer part of the chain, and the compiler version may differ. Choose the route deliberately and record which one produced the result.

## Two Rules That Hold Across Managers

### A Lockfile Establishes Manager State, Not The Runtime

A lockfile records what one manager resolved and what its commands will reuse, rewrite, or reject. It contains package identities and versions, not a process. Bun documents `bun install` as usable in existing Node.js projects ([Bun install](https://bun.com/docs/pm/cli/install)); that establishes manager capability for Bun and says nothing about whether the application runs under Bun. A pnpm project can likewise carry an explicit runtime pin, but pnpm documents `devEngines.runtime` as a separate declaration feature ([pnpm package.json](https://pnpm.io/package_json)), not as something an ordinary install reveals about the process that served the application. A type check is a further case: the compiler process has its own host runtime, and a successful check says nothing about the runtime that will load the application.

The consequence is procedural. To answer "which runtime executed this", read the invocation: the command, the shell, the executable path, its version, and its working directory. A `bun.lock` beside a `node` command is compatible evidence because the two record different layers. Do not report a runtime, a manager, or an installed state from the lockfile alone, and do not treat a runtime declaration as if it were the invoked process.

### A Declaration Does Not Prove The Active Executable

A `packageManager` field, an `engines` range, or a version-manager file such as `.nvmrc` or `.node-version` records an intention for tools that read it. None of them proves which binary the current shell resolved. Corepack's record describes the mechanism: its shims read a project's `packageManager` field when enabled and otherwise defer to a system-wide or known-good version, and its environment settings can disable project-spec enforcement or fall back to the system-wide manager ([Corepack](https://github.com/nodejs/corepack)). The same record states that Corepack shipped with Node.js from 14.19.0 up to, but not including, 25.0.0, so on the Node v26 line it cannot be assumed present unless it was installed separately. A `packageManager` field can therefore be inert, satisfied by a different installation, or overridden by configuration. npm's package.json page likewise treats `engines` as advisory unless `engine-strict` is enabled ([package.json, npm CLI v12](https://docs.npmjs.com/cli/v12/configuring-npm/package-json/)).

The consequence is to record, not infer. In the same shell and working directory as the command, capture `node --version`, the manager's own version, and the version printed by the compiler or test runner that was reached. In CI, keep the log line that shows the executable. When those records are missing, say that the declaration is the only evidence and that the active executable is unknown.

## Worked Case: A Root Command That Runs A Package Check

Suppose `/repo` contains the root manifest and workspace package above, one root `package-lock.json`, and no other lockfile in the project area. The workspace has its own config:

```json
{
  "compilerOptions": {
    "strict": true,
    "module": "nodenext",
    "moduleResolution": "nodenext"
  },
  "include": ["src/**/*.ts"]
}
```

A change to `packages/web/src/client.ts` is under review, and `npm run check:web` exits zero at `/repo`. Before explaining that result, record the following:

- **Working directory.** `/repo` for the outer command and `packages/web` for the package script, confirmed from the same shell that ran the command.
- **Exact command.** The literal `npm run check:web`, the root script text `npm run check --workspace=web`, and the package script text `tsc -p tsconfig.json --noEmit`, without normalizing the manager names or arguments.
- **Package script.** The `check` entry in `packages/web/package.json`, the package name that declares it, and the `INIT_CWD` value reported to the script.
- **Runtime version.** The `node` version and npm version from the invoking shell, plus the version printed by the compiler the script reaches. The `typescript` range in the manifest is not that record.
- **Package boundary.** The nearest `package.json` above the changed file, its `name` and `type`, and whether a nearer `package.json` exists between it and the source. Module interpretation follows the nearest package boundary, as explained in [Runtime And Project Structure](runtime-and-project-structure.md).
- **Effective TypeScript configuration.** The resolved settings and file list, for example from `tsc -p tsconfig.json --noEmit --showConfig`. TypeScript documents `--showConfig` as printing the final configuration instead of building ([TypeScript compiler options](https://www.typescriptlang.org/docs/handbook/compiler-options.html)). If the installed compiler lacks that option, read the `extends` chain and include/exclude settings directly and say which method was used.

With those records, a green exit establishes a bounded claim: npm selected the `web` workspace, found its `check` script, started the compiler that the workspace layout exposed, that compiler resolved the program described by the effective configuration, and it exited zero. Every part of that sentence is observable. Without the records, the same exit establishes only that some command succeeded in some directory.

The result still does not establish several things that readers commonly assume:

- That `packages/web/src/client.ts` was in the compiler's program. Membership comes from the effective file list, not from the file having changed; scope diagnosis belongs to `node-quality-workflow -> reference/quality-scope-and-mutation.md`.
- That the application executes on the same runtime as the compiler host. The check ran a tool; it did not run the application.
- That the compiler is the version the root lockfile records. The reached `tsc` can come from a nested or hoisted layout, and only its printed version answers that question.
- That imports resolve under the production loader. `moduleResolution` and `paths` describe the checker's model, and their limits are covered in [Runtime And Project Structure](runtime-and-project-structure.md).
- That CI or another developer runs the same command. A working directory, environment, or script edit changes the evidence.

A contrast makes the recording list useful. If the root script were `tsc -p packages/web --noEmit`, the compiler would start in the root package, resolve the project path from the root, and use the root layout. The same source files might be checked, but `INIT_CWD`, the package script, and possibly the compiler version would differ. If the workspace script did not exist, npm would fail rather than silently run a same-named root script, unless the invocation used an option that ignores missing scripts. A script name is scoped to a package even when the same name appears in several packages.

## Two Lockfiles And Other Competing Evidence

Two lockfiles in the same project area establish competing repository evidence, not the intended manager. They may show that two managers were used at different times, that a migration or import was attempted, or that a copied manifest carried its lock with it. They do not establish which file the next command will read, which tree is installed, or which runtime executes the application.

The manager's own rules decide, and those rules are manager-specific. npm documents that `package-lock.json` takes precedence over `yarn.lock` when npm considers both ([npm install, CLI v12](https://docs.npmjs.com/cli/v12/commands/npm-install/)); that is npm's resolution rule, not a statement that the repository intends npm. Bun documents lockfile migration when `bun.lock` is absent, with an order across recognized lockfiles and preservation of the original file ([Bun lockfile](https://bun.com/docs/pm/lockfile)); an import path establishes that Bun can read another manager's record, not that the resulting graph, layout, or behavior is identical. pnpm's workspace model centers on `pnpm-lock.yaml` and `pnpm-workspace.yaml` ([pnpm workspaces](https://pnpm.io/workspaces)), so a root manifest lock from another manager is not pnpm's record even when the manifest globs look familiar.

The diagnostic sequence is therefore evidence-based rather than alphabetical. Identify each file's format and version field, the manager and command that could have written it, and the workspace root the invoked manager computes. npm documents that when the current directory is inside a workspace, the workspace configuration is implicitly set and `prefix` points at the root workspace ([npm workspaces](https://docs.npmjs.com/cli/v12/using-npm/workspaces/)), so a lockfile in a parent directory can be the relevant one even when a package directory contains the files under review. Do not delete, regenerate, or edit either lockfile to resolve the ambiguity; that is a dependency-state change and belongs to `node-project-dependencies -> reference/evaluation-and-environment-changes.md`.

### The npm v12 And Bun Shrinkwrap Wording

One lockfile question remains explicitly unresolved between publishers. npm CLI v12's package-lock page states that, as of v12, npm no longer reads or writes `npm-shrinkwrap.json`. Bun's lockfile page states that Bun migrates that file, prefers it over `package-lock.json` when both are present, and does so "as npm does" ([Bun lockfile](https://bun.com/docs/pm/lockfile)). For the npm v12 boundary the two statements conflict. The inspected pages do not reconcile whether Bun reflects an older npm behavior, a different reading, or documentation drift, so this page does not choose a side.

Record the npm version and observe which command reads the file when a repository contains `npm-shrinkwrap.json`. The format-version statements have a similar shape without a single settled cross-tool meaning: npm's v12 pages list lockfile versions 1 through 3 while its `.npm-extension` page requires version 4 for extension state ([npm .npm-extension, CLI v12](https://docs.npmjs.com/cli/v12/configuring-npm/npm-extension/)), and Bun's importer lists npm lockfile versions 2 through 4. Treat `lockfileVersion` as a field to read and qualify, not as a compatibility promise.

## Limits And Version Boundaries

- **Bun capability is not runtime evidence.** Bun documents installing dependencies in existing Node.js projects, which establishes that Bun can manage such a project. It does not establish that the project executes under Bun, that Node tooling was replaced, or that the lockfile's resolutions are the ones a Node process loads.
- **Workspace syntax is not cross-manager membership.** Root `workspaces` globs, `pnpm-workspace.yaml`, `workspace:` references, negative patterns, publish-time range rewriting, and external workspace paths are documented by different publishers with different rules. A repository's `packages/*` declaration does not tell you which directories another manager would treat as members, link, expose, or script.
- **Documentation currency differs by publisher.** npm pages are pinned to CLI v12; pnpm pages are mostly unversioned, with individual features carrying annotations such as v12.7.0; Yarn Modern pages are unversioned and Yarn Classic pages identify Yarn 1; Bun package-manager pages are rolling and name versions only for particular changes. A statement here is the publisher's documented mechanism for the named version or page, not a guarantee for another installed version.
- **No execution evidence backs this page.** No install, update, lock conversion, script, or cross-manager comparison was run to produce it. The examples are hypothetical readings of documented mechanisms, and a real conclusion requires the project's own artifacts and invocation records.
- **A declaration can be stale.** A lockfile can lag the manifest, an installed tree can lag both, and a script can name a command that the layout no longer provides. Presence is not currency, and a green result is not evidence about the runtime.
- **Configuration can change selection.** Corepack environment switches, manager configuration, linker settings, and package-manager version selection can change which executable or layout a command reaches without changing any manifest text.
- **Repository utilities are separate.** The repository's deterministic utilities under `scripts/node/` have their own Bun and repository conventions. Their layout, lockfile, and invocation choices are not evidence about an application's manager.
- **No manager default or equivalence is claimed.** The page does not recommend npm, pnpm, Yarn, or Bun, does not assert that a migration preserves resolution or linking, and does not claim that two managers behave the same for a shared manifest field.

## Ownership And Routing

This page interprets manager, workspace, lockfile, layout, and invocation evidence. It does not evaluate a candidate dependency, select or migrate a manager, run an install, change a lockfile, edit a workspace declaration, or repair a script. Those actions need their owner's evaluation and the user's authorization.

- Manager behavior behind a shared field, including dependency groups, peers, optional dependencies, lock and install guarantees, and workspace linking: `node-project-dependencies -> reference/manager-semantics-and-workspace-placement.md`.
- Candidate evaluation, authorized installs, lock changes, workspace placement, and environment changes: `node-project-dependencies -> reference/evaluation-and-environment-changes.md`.
- Runtime execution, TypeScript checking, module resolution, and the canonical mixed manager-and-runtime clue case: [Runtime And Project Structure](runtime-and-project-structure.md).
- Check scope and target sets, including a changed file that is absent from a green check: `node-quality-workflow -> reference/quality-scope-and-mutation.md`.
- Production behavior changes that must respect the recorded runtime, manager, and invocation: `node-project-writer -> reference/change-design-and-validation.md`.
- Project structure and outcome planning around workspaces: `node-domain-planning -> reference/project-structure.md`.

When an observation cannot be tied to a manager version and an invocation, report that gap. A declaration is not a substitute for the executable, and the correct answer is often that the project evidence supports a narrower claim than the one requested.
