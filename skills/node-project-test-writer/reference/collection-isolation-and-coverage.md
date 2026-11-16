# Collection, Isolation, And Coverage

Three questions share one evidence chain but have different answers: why was this test omitted from the run, does this process case leak state, and why did coverage change after a test move. Collection is runner discovery, isolation is a boundary the runner defines, and measurement is a provider and configuration over a source universe. A run's count of passed assertions says nothing about which cases were collected, and a coverage percentage says nothing about whether those assertions detect a wrong result. Keep collection, isolation, measurement, and assertion strength separate when reporting.

What a test should prove, how faithful a double must be, and whether an assertion is strong enough are design questions: they belong to [Test Design And Measurement](test-design-and-measurement.md). This page owns discovery, isolation, process cases, and coverage interpretation, including the canonical coverage-drop diagnosis.

## Test Discovery And Isolation

Collection is part of the evidence. Check that the requested cases and parameterized variants were discovered under the actual command and filters. "No tests collected," deselected cases, or skipped paths do not establish that behavior passed, and a filtered-out case cannot fail. Preserve existing test layout and discovery conventions rather than migrating them as incidental work.

### Diagnose An Omitted Test

Establish the invocation before theorizing about the framework:

- the exact script or wrapper that ran, including arguments;
- the working directory the runner used;
- the runner and its installed version;
- the configured test root and the file-name pattern or glob that decides collection;
- any positional or name filter applied to this run; and
- the collected, skipped, and filtered counts the runner reported.

A missing case is usually a mismatch between one of those inputs and the file, not a defect in the test body. Three concrete mismatches cover most reports.

**A `.test.ts` file is not collected when the runner's pattern depends on Node's native type stripping and stripping is disabled.** [Node.js v26.13.0](https://nodejs.org/download/release/v26.13.0/docs/api/test.html) documents JavaScript test-file patterns, and adds the `.ts`, `.mts`, and `.cts` variants only when native type stripping is enabled; `--no-strip-types` suppresses those variants. On that path the runner [strips erasable syntax](https://nodejs.org/download/release/v26.13.0/docs/api/typescript.html) by replacing inline types with whitespace, does not type-check, ignores `tsconfig.json`, does not accept `.tsx` in the documented native path, and errors on syntax that requires code generation. So a command that starts Node with type stripping disabled collects the JavaScript patterns and silently omits the TypeScript ones. The evidence to report is the runner version, the stripping flag actually in effect, the effective pattern, and the collected count — not "the test did not run."

**A `*.spec.ts` file is not collected when the runner's documented default patterns name `test` shapes only.** Node.js v26.13.0's documented patterns are built from `test` file names and `test/` directories; a `.spec` file is collected only when it is passed as a path, matched by a configured pattern, or run by a runner whose documented defaults include `.spec` — Jest 30.5 documents both `.test` and `.spec` shapes, and Bun documents its own TypeScript, JavaScript, and JSX-family patterns. Check the effective pattern in the runner that actually executed; a filename convention that works in one runner is not evidence about another.

**A Bun path filter is a substring, not a glob.** [Bun documents](https://bun.com/docs/test/discovery) positional path arguments as substring filters over the discovered paths, so `bun test cart` also selects files such as `src/checkout/cart-total.test.ts`, and a positional argument written to look like a glob is not interpreted by the runner as a glob. A filter that over-selects hides the omission by running adjacent cases; a filter that matches nothing produces "no tests" while the file is present and valid. Use the runner's documented filter form and report the filter string, not just the intent.

When the omitted file is one of several parameterized cases, also confirm that the variant enumeration produced the expected number of runs. A file that is collected while its table cases are empty still reports success with nothing exercised.

### Isolation Boundaries

Isolation is runner-specific and usually describes one boundary: a process, a global and module registry, a test environment, or a worker. None of them resets an external database, a service, a port, or the filesystem.

- Node.js v26.13.0 documents process-level isolation by default for `node --test`, with each matching file in a child process; its API can also set isolation to `none`, in which case files are imported into the runner process and share a context. That is file and process isolation, not a statement that every test or resource is isolated.
- Bun documents a shared process, global object, and module registry by default. `--isolate` gives each file a fresh global and module registry; `--parallel` runs files in worker processes and implies isolation unless `--no-isolate` is supplied, while within-file concurrency is a separate control. Bun also documents per-file cleanup of selected process resources between isolated files.
- Jest 30.5 gives each test suite its own `TestEnvironment` instance and module registry by default, with child-process workers as the documented default mechanism and worker threads experimental; `resetModules` changes module-registry lifetime again per test.

Two cases that pass alone and fail together are the standard leak signal. In one form, a case resolves a fixture path relative to `process.cwd()` and a second case changes the working directory, so the first reads a different file depending on order; run each file alone in the same command shape, then run both in one process, then reverse the order. In the other form, a case sets a value on `process.env` in a `beforeAll` hook without restoring it, and a second case asserts a default that the leaked value overrides. If each case is green alone and the pair is red together, the shared mutable value is the first suspect, regardless of how the runner describes isolation. If Node's process-per-file mode still correlates the failures, look outside the process: a fixed port, a shared temporary path, a service-level singleton, or a stale artifact is the boundary that leaked.

Choose fixture and helper lifetime to match resource lifetime. Shared mutable state, environment or working-directory changes, timers, background work, and external services can leak across cases even when a runner isolates files. Give each acquired resource a cleanup path, including when later setup fails — a teardown registered only after a successful setup is skipped exactly in the failure case that needs it. Avoid test-order dependence and arbitrary sleeps; wait on observable completion or use the project's deterministic seam.

## CLI And Process Cases

When the contract includes a CLI, test its observable interface: arguments and options, output streams, exit status, and the environment and working directory where they matter. The process API and shell behavior are platform-dependent, so assert what the contract promises rather than incidental formatting.

For Node child-process tests, `execFile()` does not use a shell by default while `exec()` does; that difference changes quoting, metacharacter handling, and which error surfaces for a bad argument. `spawn()` exposes streams and a close event, so a large or long-running output can be consumed incrementally instead of buffered. Captured output is bounded: [Node documents](https://nodejs.org/api/child_process.html) a `maxBuffer` default for buffered child output, and a child that fills a pipe before the parent reads can block, so a finite capacity is a relevant input to any test that asserts on output. Captured output, exit code, invocation environment, and program arguments should each be asserted from the value the process actually received.

Use the project's established helper and avoid introducing a shell or a test-harness change without authorization. A test that reaches a real shell can pass while the direct invocation fails, and a test that asserts only an exit code can pass while the wrong stream carried the result.

## Coverage Interpretation

Coverage reports describe execution over a tool-configured file universe and structural metric; they do not establish that assertions detect incorrect behavior. Interpret a percentage only with its measurement context:

- runner and provider, with version when known;
- source universe, and whether unvisited files or test files are included;
- line, branch, function, statement, or other reported metric;
- include and exclude patterns, ignore directives, and configured thresholds; and
- whether data was freshly collected for the tests being compared.

The denominator is a weighted count of the measured items — lines, statements, branches, or functions — and the total is a metric-specific ratio of summed covered counts to summed totals. It is not a file count and not a per-file average, so adding one small uncovered file and one large well-covered file moves a total differently from adding two equal ones. What counts as a measured item also differs by provider: Node v24.18.0 counts every physical source line, including blank and comment lines, while Bun reports executable lines and Istanbul-based reporting records instrumenter statements and branches. An empty file's own ratio is provider-defined; Node's percentage helper returns 100 when the total is zero. Do not compare a line percentage from one provider with a branch percentage from another.

Unvisited source and erased source both move the denominator. A loaded-file report omits files the tests never reached, so the percentage describes the loaded subset; an all-files mode adds matching unvisited files with zero covered counts, and their measured items still enlarge the denominator, which is why the ratio falls rather than staying a statement about only the visited files. Read a total that moved while no covered line changed as a denominator event until the file set proves otherwise: that is the diagnostic for a percentage drop that is misread as a behavior change. A source line that survives only as an erased type construct can also enter the count: under source-map remapping in Node v24.18.0, an erased `import type` line was reported uncovered, lowering the percentage without any covered line losing execution, and a later upstream change addresses that behavior — check the installed revision rather than assuming either outcome.

Defaults and documented wordings are not interchangeable. c8 documents loaded-file coverage by default and `--all` to include matching files under configured source directories. Node.js v26.13.0 documents built-in test coverage behind `--experimental-test-coverage`, marks it experimental, and exposes its own include and exclude globs; its API says matching test files are excluded by default, while an unversioned Node Learn sample includes one in its total, and the cited pages do not explain the difference — preserve that uncertainty rather than choosing a denominator. Bun documents line and function metrics with source maps, excludes test files by default, and documents no all-files mode in the inspected pages; its coverage page says that outside `--parallel` threshold checking runs only when the text reporter is enabled, while its test-configuration page says the check applies with any reporter, and the inspected pages do not reconcile the two. Jest collects coverage only when configured and exposes Babel and V8 providers.

Use uncovered lines or branches as investigation leads: identify the behavior, add an assertion for its contract when in scope, and collect a fresh report. Do not change coverage configuration or the denominator merely to raise a total. A configured threshold is a project gate, not a universal quality target.

### Which Source Path A Provider Reports

The report key is the executed module URL; a resolvable source map switches that key to the original source path. Position-preserving execution makes the map unnecessary, while a position-changing transform needs it for accurate coordinates.

- **c8 v12.0.0** [remaps](https://github.com/bcoe/c8) generated code to original source files when a map is present and resolvable, and otherwise keeps the executed path. Its default extension list includes `.ts` and `.tsx`, which makes them eligible, not selected: selection is decided by the include and exclude stage. By default that stage filters the executed path before remapping; `--exclude-after-remap` moves the whole extension, include, and exclude decision after remapping, so it changes inclusion as well as exclusion despite its name. `--all` globs the configured source roots on disk and filters those source files directly. `sourcesContent: false` or an unreachable original source degrades remapping and can mislabel the report.
- **Node** reports a natively type-stripped `.ts` module as `.ts` because stripping preserves positions. Compiled output that the process executes is reported under its executed `.js` path unless `--enable-source-maps` is set, in which case the report is remapped to the original `.ts`. The API reference describes exclusions and reporters but not coverage remapping, so verify the flag's effect against the installed runtime.
- **Jest 30.5.2** [maps](https://jestjs.io/docs/configuration) through the transform's source map: the Babel provider instruments with the input map when the transform produced one, and the V8 provider needs the transform's stored map on disk to remap; without a map it reads the executed file. A file that no transformer claims falls back to type stripping, which preserves positions and needs no map.
- **Bun** [transpiles](https://bun.sh/docs/test/coverage) by default and uses its internal source map unless `coverageIgnoreSourcemaps` is set, so it reports loaded `.ts` files under their original names.

Filename identity is not coordinate accuracy. A report can carry a `.ts` name with wrong line and column coordinates, and can carry correct `.ts` coordinates with no source map at all — Node's native stripping is the second case, and a transpiler that retains the `.ts` name while changing layout is the first. On Bun 1.3.14, setting `coverageIgnoreSourcemaps = true` kept the row name `mod.ts` while the reported percentage moved from 66.67% to 75.00%, because the coordinates and the counted items came from Bun's internal representation under the original name. Selecting files by a `.ts` name is therefore a separate decision from trusting a percentage computed at those coordinates.

A `.ts` include glob cannot match an executed `.js` path. In Node, include and exclude globs apply to the executed URL before remapping and again to the remapped source URL when source maps are enabled, so a file must pass both filters to appear under its source name; supplying a `--test-coverage-exclude` value also replaces the default test-file exclusion, which brings test files back unless they are excluded again. In c8, selecting a compiled `.ts` source path requires `--exclude-after-remap` or an `--all` glob over the source tree. Either way, an empty or unexpectedly small report is a filter-stage question before it is a coverage question.

## Diagnose A Coverage Drop After Moving A Test

This page is the canonical home of the coverage-drop diagnosis. `node-project-reference -> reference/test-execution-and-measurement.md` owns the cross-runtime interpretation rule and the runner and coverage view across runtimes; the worked case and the recording list below stay here.

Treat a percentage change as a symptom, not proof of a behavior regression. Compare fresh runs using the same command, runner and provider, version, filters, and source and test revisions. Then inspect what was collected and which source files contribute to the denominator before interpreting the aggregate.

For example, suppose moving a test changes a report from 100% to 67% while production source was not edited. First establish whether the intended test was collected in both runs: a moved file may no longer match the discovery pattern for its new directory, may be excluded by a path filter, or may no longer be reached by a name filter. This is a collection question, and the omitted-test evidence above applies unchanged. If collection is unchanged, compare the effective source file set and include and exclude rules. A loaded-file report can omit source that the tests no longer reach, while an all-files report can add unvisited files at zero coverage. A changed denominator can therefore lower the percentage without any previously covered line becoming uncovered.

A move also changes what is loaded. Compare the moved test's imports before and after the move: a relative specifier that resolves differently at the new depth, a dropped barrel import, or a helper that used to be imported for its side effect all remove modules from a loaded-file universe, and those modules leave the report with the coverage they used to contribute. The same comparison exposes the opposite failure: a moved test that now imports a second copy of a module through a different path exercises a different instance while the originally reported file keeps its old percentage.

Record the comparison before concluding anything:

- the exact invocation, including arguments and the wrapper or package script;
- the working directory;
- the installed tool and runtime version, including the coverage provider and its version;
- the discovery count, including skipped or filtered cases;
- the coverage provider and configured source roots;
- the include and exclude patterns in effect;
- the reported metric and any configured threshold; and
- whether old coverage data was removed or overwritten.

Then read the result in one of three ways.

1. **Collected tests differ.** Report the collection change; the coverage difference is a consequence of the filter or pattern, not of the moved test's behavior. Fix the collection input only if the intended case was meant to run.
2. **Collection is unchanged and the source universe differs.** Report denominator drift. Compare matching files and metrics, and state that unvisited or unloaded files entered or left the measured set, before deciding whether coverage behavior changed.
3. **Collection and source set are unchanged, but a covered line or branch lost execution.** Inspect the moved test's setup and import path and the behavior it actually exercises. Add or adjust assertions only when they verify the requested contract.

Do not change exclusions or thresholds to make the number recover. A recovered total reached by removing unvisited files or lowering a gate has not answered which behavior stopped executing.

Illustrative commands, not project defaults:

```sh
# Node.js v26.13.0 built-in coverage; the coverage option is experimental there.
node --experimental-test-coverage --test

# c8 with source roots matching the measured TypeScript tree.
c8 --all --src=src --include='src/**/*.ts' --exclude='src/**/*.test.ts' node --test
```

The first command's coverage option is experimental in the cited Node.js v26.13.0 documentation. The c8 line is qualified by its configured source roots: `--all` globs whatever `--src` names, so the illustration is only correct for a project whose TypeScript sources live under `src`. c8 options and defaults are version- and configuration-sensitive, and neither example has been run against a project. Retain the repository's configured command and report when its effective file set cannot be established. See the [Node.js v26.13.0 test-runner documentation](https://nodejs.org/download/release/v26.13.0/docs/api/test.html) and the [c8 project documentation](https://github.com/bcoe/c8) for publisher-described behavior.

## Limits And Routes

Node test-file patterns for TypeScript depend on native type stripping and its enabled state, and Bun's patterns follow its own rolling documentation. Coverage percentages depend on source selection, metric, and provider; no percentage threshold, provider default, or cross-provider denominator follows from anything here. Coverage measures execution over a configured universe, so a passing run and a high percentage remain separate from assertion strength: neither establishes that a wrong result would be detected.

This is test-only work. Standalone quality configuration routes to `node-quality-workflow`; package tarball or installed-archive consumer questions route to `node-package-distribution`; and tests for this repository's `scripts/node/` utilities stay on their repository route, `skill-script-node-test-writer`. When a diagnosis identifies a production defect, preserve the failing assertion and hand off the production change rather than editing production code under a test-only request.
