# Test Execution And Measurement

## Scope

This page interprets three questions about a TypeScript test run: was this test collected and executed, does a changed coverage percentage reflect a behavior change, and does a passing test prove the contract. It owns runner, collection, and coverage interpretation across Node.js, Bun, and Jest, and it keeps collection, isolation, assertion strength, and measurement as separate pieces of evidence.

The subject is TypeScript source, TypeScript tests, and TypeScript coverage output in Node.js or Bun projects. JavaScript-only work is out of scope, and this page excludes JavaScript or mixed-language eligibility, `allowJs` and `checkJs` guidance, JavaScript diagnostics, and JSDoc typing of `.js` files. Each statement stays with its named runner, provider, version, mode, or configuration, because the cited pages are version-pinned or rolling and either kind can change.

Test design, assertion adequacy, test edits, and the full discovery and coverage-drop procedures belong to `node-project-test-writer` in its `reference/test-design-and-measurement.md` and `reference/collection-isolation-and-coverage.md` pages. Program and target-set interpretation belongs to [Quality Scope And Tool Effects](quality-scope-and-tool-effects.md), and what executes the code belongs to [Runtime And Project Structure](runtime-and-project-structure.md). This page states passive mechanisms and grants no tool, write, or completion authority.

## Collection Rules Per Runner

Collection is discovery plus the patterns, filters, and working directory in force for one invocation. Each runner defines its own rules, and an installed package manager or a TypeScript-capable runner does not establish either the test runtime or type checking.

### Node.js

Node.js v26.13.0 documents `node --test` filename patterns built from `test` file names and `test/` directories ([Node.js v26.13.0 test runner](https://nodejs.org/download/release/v26.13.0/docs/api/test.html)). The `.ts`, `.mts`, and `.cts` variants are added only when native type stripping is enabled; `--no-strip-types` suppresses those variants. On that path Node replaces erasable type syntax with whitespace, does not type-check, ignores `tsconfig.json`, does not accept `.tsx`, and errors on syntax that would require generating JavaScript ([Node.js v26.13.0 TypeScript modules](https://nodejs.org/download/release/v26.13.0/docs/api/typescript.html)).

Two collection consequences follow for that version and path. A command that starts Node with stripping disabled collects the JavaScript patterns and silently omits the TypeScript ones, so the file exists, the run is green, and the case never executed. A `.spec.ts` file matches no documented default pattern there unless it is passed as a path, matched by a configured pattern, or run by a runner whose documented defaults include `.spec`. Relative patterns and default roots resolve from the working directory of the invocation, so a package script or wrapper that changes directory changes discovery as well.

### Bun

Bun documents JavaScript, TypeScript, and JSX-family discovery patterns, recursive scanning, positional path arguments, test-name filtering, and root and ignore configuration ([Bun test discovery](https://bun.com/docs/test/discovery)). The positional-argument rule behaves unlike its name suggests: such arguments are substring filters over the discovered paths, not globs, so `bun test cart` also selects a file such as `src/checkout/cart-total.test.ts`, and an argument written to look like a glob is not interpreted as a glob. The scan starts from the working directory or a configured root, so invoking `bun test` from a subdirectory narrows what can be discovered. Tests execute in the Bun runtime, and `bun test --check` is a separate interface that checks test files and their imports before tests run ([Bun test CLI](https://bun.com/docs/cli/test)).

A filter that over-selects hides an omission by running adjacent cases, while a filter that matches nothing reports "no tests" for a file that is present and valid. Record the filter string that was used, not the filter that was intended. Bun's test pages were rolling and surfaced no release version, so these descriptions are the accessed documentation rather than a contract for a specific Bun release.

### Jest

Jest 30.5 documents default `testMatch` patterns that include `.test` and `.spec` names, files under `__tests__`, and the extensions `.js`, `.jsx`, `.ts`, `.tsx`, `.mjs`, `.cjs`, `.mts`, and `.cts`; configuration can change that selection ([Jest configuration](https://jestjs.io/docs/configuration)). The default test environment is Node.js, while the transform pipeline decides how a `.ts` file is produced. Jest v30.5.2 records type stripping for `.ts`, `.mts`, and `.cts` files that no transformer claims, which is a version-specific release behavior and not a claim that Jest type-checks those files.

Jest collection therefore depends on three inputs that are easy to conflate: the effective pattern, the configured roots and test-path settings, and the transformer registration. Roots resolve from the root directory, which defaults to the directory holding the configuration, so the working directory used to invoke Jest and the configuration location can select different files. A file that matches the pattern but fails transformation is a different failure from a file the pattern never selected, and neither is a statement about the test body.

### What Collection Evidence Establishes

"No tests collected," deselected cases, and skipped paths do not establish that behavior passed, and a filtered-out case cannot fail. Before interpreting a run, record the exact script or wrapper and its arguments, the working directory, the runner and its installed version, the effective file-name pattern or glob, any positional or name filter, and the collected, skipped, and filtered counts the runner reported. A filename convention that works in one runner is not evidence about another: Node's default shapes, Jest's `testMatch`, and Bun's recursive scan are separate rules.

## Runtime, Transformation, And Type Checking

The runner chooses the execution runtime, and the transformation step is not the checking step. `node --test` executes tests in Node.js; `bun test` executes them in Bun; Jest's default environment is Node.js with a transform stage in front of it. TypeScript acceptance by a runner means transformation only: Node strips erasable syntax without checking, Bun transpiles before running and offers `--check` and `bun check` as separate checking interfaces that exit non-zero on error ([Bun type checking](https://bun.com/docs/runtime/check)), and Jest documents that Babel can transpile TypeScript without verifying its types ([Jest code transformation](https://jestjs.io/docs/code-transformation)).

The observable consequence is that a green suite establishes the selected execution and its assertions, not that the program type-checks. A runtime transform also changes line layout, which matters later in this page: a line-preserving strip is not the same measurement input as a transpilation that rewrites positions. Which program a separate check covers is interpreted in [Quality Scope And Tool Effects](quality-scope-and-tool-effects.md).

## Isolation And Cleanup Boundaries

Isolation is runner-specific and describes one boundary. None of the documented boundaries resets an external database, a service, a port, or the filesystem.

- Node.js v26.13.0 documents process-level isolation by default for `node --test`, with each matching file in a child process; its API can also set isolation to `none`, in which case files are imported into the runner process and share a context. That is file and process isolation, not a statement that every test or resource is isolated.
- Bun documents a shared process, global object, and module registry by default. `--isolate` gives each file a fresh global and module registry, `--parallel` runs files in worker processes and implies isolation unless `--no-isolate` is supplied, within-file concurrency is a separate control, and isolated files get per-file cleanup of selected process resources ([Bun test CLI](https://bun.com/docs/cli/test)).
- Jest 30.5 gives each test suite its own `TestEnvironment` instance and module registry by default, with child-process workers as the documented default mechanism and worker threads experimental; `resetModules` changes module-registry lifetime again before each test ([Jest configuration](https://jestjs.io/docs/configuration)).

Read those against four boundaries. Process state covers globals, module registries, and open handles. The working directory covers relative paths resolved through `process.cwd()`. Environment covers inherited and mutated variables. Resources cover files, ports, timers, servers, and subprocesses the test acquired. A case that resolves a fixture path from `process.cwd()` and a second case that changes the directory disagree about which file they read, and a value set on `process.env` in a setup hook without restoration overrides a later default; both pairs pass alone and fail together even when the runner isolates files. If a process-per-file runner still correlates the failures, the boundary that leaked is outside the process.

Cleanup is a place to release what the test acquired, and a teardown registered only after a successful setup is skipped exactly in the failure case that needs it. Node documents `after` as guaranteed even when tests in the suite fail and `afterEach` as running even when its test fails, while global setup and teardown are marked early development and global teardown is not called if global setup throws; Bun documents `onTestFinished` running after `afterEach` and as unsupported for concurrent tests. Fixture and helper lifetime design belongs to `node-project-test-writer`.

## Assertion Strength Compared With Execution Measurement

Coverage counts execution of measured items; an assertion compares a computed value with an expected one. These are different observations of the same run. A line can be executed and counted while the assertion beside it is too weak to detect a wrong result:

```ts
import { test, expect } from "node:test";

test("applies the discount", () => {
  const total = applyDiscount(100, 0.2);
  expect(total).toBeDefined(); // covers the line; a wrong total still passes
});
```

Replacing the second statement with `expect(applyDiscount(100, 0.2)).toBe(80)` converts the same covered line into a contract check. The consequence is that a passing suite and a high percentage are not composed evidence: the executed line contributes to the numerator, and the weak assertion passes for any defined number. Which assertion is strong enough is a design question owned by `node-project-test-writer -> reference/test-design-and-measurement.md`.

## The Coverage Denominator

### The Interpretation Rule

An aggregate coverage change is not interpreted before the file set and the provider are compared. A percentage is a ratio over a filtered universe, so the same source can move it without any behavior changing, and different providers can report different numbers for the same execution. The coverage-drop diagnosis after a test move, including its recording list and its three readings, is canonical in `node-project-test-writer -> reference/collection-isolation-and-coverage.md`; this page keeps the interpretation rule and the provider view rather than restating that diagnosis.

### What The Denominator Counts

The denominator is a weighted count of the measured items, and the reported total is a metric-specific ratio of summed covered counts to summed totals. It is not a file count and not a per-file average, which is why adding one small uncovered file and one large well-covered file moves a total differently from adding two equal ones. What counts as an item differs by provider: Node v24.18.0 counts every physical source line, including blank and comment lines, while Bun reports executable lines and Istanbul-based reporting records instrumenter statements and branches ([Node.js v24.18.0 coverage implementation](https://github.com/nodejs/node/blob/v24.18.0/lib/internal/test_runner/coverage.js), [Bun coverage](https://bun.sh/docs/test/coverage)). An empty file's own ratio is provider-defined; Node's percentage helper returns 100 when the total is zero. No cross-provider denominator parity follows from any of this, and a line percentage from one provider should not be compared with a branch percentage from another.

### Loaded Files Compared With All Files

Loaded-file measurement is the default for c8, Node's built-in coverage, Bun, and Jest without `collectCoverageFrom`. c8 states that V8 supplies coverage only for files the engine loaded; Node merges V8 coverage for loaded scripts and filters it by its default excludes; Bun states that coverage only tracks files that are loaded; Jest without `collectCoverageFrom` covers the files the suite loaded.

All-files measurement is opt-in and version-bound. c8's `--all` together with `--src` adds matching unvisited files at zero. Node's current documentation (v26.13.1) describes `coverageIncludeAll` on the `run()` API, default `false`, to include never-loaded source found under the working directory and subject to the same globs, while that option and a matching CLI flag were absent from v24.18.0 ([Node.js test runner](https://nodejs.org/api/test.html)). Jest's `collectCoverageFrom` collects coverage for matching files that no test required, instrumenting them at zero if untouched. Bun documents no all-files mode on the inspected pages.

The consequence is arithmetic: an unvisited file added by an all-files mode contributes its measured items to the denominator and zero to the numerator, so the ratio falls rather than remaining a statement about the visited files. A total that moves while no covered item changed is a file-set and configuration question first.

### Include And Exclude Controls And Their Stage

The include and exclude controls decide which paths the provider measures, and the stage at which they apply decides which path they see.

- c8 v12.0.0 delegates filtering to `test-exclude`, whose `shouldInstrument` decides on extension, include, and exclude together. In a default run the filter applies before remapping, to the executed path, with no post-remap filter; `--exclude-after-remap` keeps the pre-remap scripts and applies the same decision after remapping, to the source path. The flag's name says "exclude," but it moves the whole extension, include, and exclude decision, so it changes inclusion as well as exclusion. `--all` globs the configured `--src` directories on disk and filters those source files directly. `sourcesContent: false` or an unreachable original source degrades remapping and can mislabel the report ([c8](https://github.com/bcoe/c8)).
- Node applies its include and exclude globs to the executed URL before remapping and again to the remapped source URL when `--enable-source-maps` is on, so a file must pass both filters to appear under its source name. Supplying any `--test-coverage-exclude` value replaces the default test-file exclusion, which brings test files back unless they are excluded again.
- Jest's `collectCoverageFrom` is order-sensitive, with later positive patterns overwriting earlier negations; `coveragePathIgnorePatterns` defaults to the `node_modules` path segment, and `forceCoverageMatch` re-includes test-named files.
- Bun exposes path ignore patterns and skips test files by default, and its defaults also exclude `node_modules` and files loaded through non-JavaScript or non-TypeScript loaders.

A `.ts` include glob cannot match an executed `.js` path, so an empty or unexpectedly small report is a filter-stage question before it is a coverage question. c8's release artifacts are pinned at v12.0.0, while its filter and remap dependencies were inspected off a release tag, so dependency behavior is not release-pinned; c8 is a collector and reporter, not a test runner, and no compatibility with a particular Bun invocation or TypeScript transform follows.

## Omitted Tests, c8, And The Node Built-In Interface

### A TypeScript Test File That Is Never Collected

Take a repository whose test script runs `node --test` with type stripping disabled and a file named `src/cart.test.ts`. Node v26.13.0 adds the TypeScript pattern variants only when native stripping is enabled, so the invocation collects the JavaScript patterns, reports a green run, and omits the case. The evidence to report is the runner version, the stripping flag actually in effect, the effective pattern, and the collected count, not "the test did not run." Two qualifications keep the case honest: the behavior belongs to that pinned version and path, and a `.spec.ts` name would additionally need a pattern or an explicit path. The full discovery and omission procedure belongs to `node-project-test-writer -> reference/collection-isolation-and-coverage.md`; the runner rule is the part this page keeps.

### A Covered Line With A Weak Assertion

The weak-assertion form above is a measurement case rather than a collection case: the line is collected, executed, and counted, and the assertion passes without comparing the contract value. A coverage report cannot distinguish that line from one whose assertion would fail on a wrong result, so uncovered lines are investigation leads and covered lines are not proof of assertion strength.

### c8 Loaded Files And The `--all` Option

c8 v12.0.0 documents loaded-file coverage by default and `--all` to add files under configured source roots that pass the include, exclude, and extension filters, reporting unvisited matches at zero ([c8](https://github.com/bcoe/c8)). The illustrative command below is qualified by its source roots: `--all` globs whatever `--src` names, so it is only correct for a project whose TypeScript sources live under `src`, c8 defaults are version- and configuration-sensitive, and the command has not been run against a project.

```sh
# c8 with source roots matching the measured TypeScript tree.
c8 --all --src=src --include='src/**/*.ts' node --test
```

Read a percentage of zero on a file listed this way as a universe entry, not as a failed test.

### The Node Built-In Coverage Interface

Node v26.13.0 documents a separate built-in coverage interface behind `--experimental-test-coverage` and marks it experimental; its API says matching test files, Node core modules, and `node_modules` files are excluded by default with include and exclude controls, and it exposes line, branch, and function coverage ([Node.js v26.13.0 test runner](https://nodejs.org/download/release/v26.13.0/docs/api/test.html)). This is a runtime interface, not a third-party collector: its defaults, its include and exclude stage, and its version-bound `coverageIncludeAll` capability belong to Node, and c8's or Jest's defaults do not transfer to it.

## Which Source Path A Provider Reports

The report key is the executed module URL, and a resolvable source map switches that key to the original source path. Position-preserving execution makes the map unnecessary; a position-changing transform needs it for accurate coordinates. The four providers implement that rule differently.

- **c8 v12.0.0** remaps generated code to original source files when a source map is present and resolvable, and otherwise keeps the executed script path. Its default extension list includes `.ts`, `.tsx`, `.jsx`, `.js`, `.cjs`, and `.mjs`, which makes TypeScript files eligible rather than selected: selection is decided by the include and exclude stage ([c8](https://github.com/bcoe/c8)).
- **Node** reports a natively type-stripped `.ts` module as `.ts` because stripping replaces inline types with whitespace and preserves positions. Compiled output that the process executes is reported under its executed `.js` path unless `--enable-source-maps` is set, in which case it is remapped to the original `.ts`. The API reference describes exclusions and reporters but not coverage source-map remapping, so verify the flag's effect against the installed runtime. On Node v24.18.0, enabling source maps also exposed an erased `import type` source line reported uncovered, and a later upstream change addresses that behavior; presence of the fix is decided per revision, not assumed for any release ([Node.js v24.18.0 coverage implementation](https://github.com/nodejs/node/blob/v24.18.0/lib/internal/test_runner/coverage.js)).
- **Jest 30.5.2** maps through the transform's source map. The Babel provider instruments with the input map when the transform produced one, and the V8 provider needs the transform's stored map to remap; without a map it reads the executed file. A file that no transformer claims falls back to type stripping, which preserves positions and needs no map ([Jest code transformation](https://jestjs.io/docs/code-transformation)).
- **Bun** transpiles by default, generates an internal source map, and reports loaded `.ts` files under their original names; `coverageIgnoreSourcemaps` disables that use. Because Bun transpiles, the `.ts` name alone does not guarantee accurate coordinates: on Bun 1.3.14, setting `coverageIgnoreSourcemaps = true` kept the row name `mod.ts` while the reported percentage for the same fixture moved from 66.67% to 75.00%, because the coordinates and counted items came from the transpiled representation under the original name ([Bun coverage](https://bun.sh/docs/test/coverage)).

Filename identity is not coordinate accuracy. A report can carry a `.ts` name with wrong line and column coordinates, and it can carry correct `.ts` coordinates with no source map at all; Node's native stripping is the second case, and a transpiler that retains the `.ts` name while changing layout is the first. Conversely, a transformer may resolve an original `sources` entry that is itself generated output, so the report is only as truthful as the map. Selecting files by a `.ts` name is therefore a separate decision from trusting a percentage computed at those coordinates.

## Visible Disagreements

### Node Coverage-File Inclusion

The pinned Node v26.13.0 API says matching test files are excluded from coverage by default, while the rolling Node Learn coverage example includes `main.test.js` in its displayed report; the inspected pages do not explain the difference, so both sides stay visible here ([Node.js v26.13.0 test runner](https://nodejs.org/download/release/v26.13.0/docs/api/test.html), [Node.js Learn coverage](https://nodejs.org/learn/test-runner/collecting-code-coverage)). The bounded v24.18.0 interface explains the pattern without settling the example: supplying an explicit exclude flag replaces the default test-file exclusion, so a run that passes its own exclude value can include test files. That accounts for how the two observations can coexist; it does not establish what the Learn page's unspecified invocation did, so no denominator is chosen for it.

### Bun Thresholds And Reporters

Bun's coverage page states that, outside `--parallel`, threshold checking only runs when the text reporter is enabled, that an lcov-only run currently exits zero regardless of the threshold, that omitted line and function keys retain a 0.9 default, and that `statements` is accepted but unenforced. Its test-configuration page states that the check applies with any coverage reporter. Both are first-party pages, no Bun run resolves the difference here, and it reads as an omission in the generic page rather than a demonstrated contradiction. The operational consequence is that a Bun coverage threshold is not a reliable gate unless the documented reporter and mode conditions are met.

### No Cross-Provider Denominator Parity

The providers also disagree legitimately about what a line is: Node v24.18.0 counts physical source lines, Bun reports executable lines, and Istanbul-based reporting records instrumenter maps. These are different measured universes, so a percentage from one provider and a percentage from another are not comparable, and a threshold carried from one is a project policy choice rather than a property of the code.

## Limits And Ownership

Jest behavior depends on the configured transformer: a transform that returns no map yields generated coordinates, and `transpileOnly` is an option of specific TypeScript transformers such as ts-jest and ts-node, not a Babel option. Bun's `--check` checks test files and their imports only, so it does not establish a whole-project check. Whether a provider reports `.ts` or emitted `.js` is stated per provider above and never as a universal rule. c8 was inspected from its pinned source and tests rather than executed for this page; Jest is bounded to v30.5.2; Node behavior is bounded to the v24.18.0 interface and the cited v26.13.0 and v26.13.1 documentation; Bun pages are rolling and the bounded observations are pinned to Bun 1.3.14. No runner, provider, or project command was executed for this page, and no coverage measurement of a real project is claimed.

This page owns interpretation only. Test design, assertion adequacy, and test edits go to `node-project-test-writer`, whose `reference/test-design-and-measurement.md` and `reference/collection-isolation-and-coverage.md` own their subjects. Standalone quality configuration and diagnostic work go to `node-quality-workflow`, including the missing-file diagnosis in `node-quality-workflow -> reference/quality-scope-and-mutation.md`. A production defect exposed by a test is reported to `node-project-writer` rather than repaired under a test-only request. Dependency, lockfile, manager, and runtime-selection changes go to `node-project-dependencies`, and package-artifact or consumer-declaration problems go to `node-package-distribution`. Tests for this repository's `scripts/node/` utilities stay on their repository route, `skill-script-node-test-writer`, and that route's Bun, coverage, and layout conventions are not general project defaults.

Runtime execution, module resolution, and the mixed manager-and-runtime reading are covered in [Runtime And Project Structure](runtime-and-project-structure.md). Which program a check covered, and whether a quality command wrote files, is covered in [Quality Scope And Tool Effects](quality-scope-and-tool-effects.md). No step in this page selects or relies on Vite, and no command sequence here forms an implicit pipeline; an incidental dependency edge is neither direct selection evidence nor proof of graph absence. No cross-runner equivalence, compatibility promise, universal threshold, or whole-project coverage follows from a green suite or a percentage ([Node.js v26.13.0 test runner](https://nodejs.org/download/release/v26.13.0/docs/api/test.html), [Jest configuration](https://jestjs.io/docs/configuration), [Bun coverage](https://bun.sh/docs/test/coverage)).
