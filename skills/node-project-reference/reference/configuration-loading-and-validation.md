# Configuration Loading And Validation

## Scope

This page answers which source supplied a configuration value, whether a file was actually loaded, and whether the resulting value was validated. It covers environment variables, Node.js and Bun environment-file loading, programmatic loading and parsing, and application-level interpretation in TypeScript projects. The subject is TypeScript source, configuration, declarations, tests, quality diagnostics, and package artifacts in Node.js or Bun projects. JavaScript-only work is out of scope, and the JavaScript checking options `allowJs` and `checkJs`, together with JSDoc typing of `.js` files, are excluded from this reference.

The page states passive mechanics and interpretation. It does not read, edit, or validate a project's configuration, and it does not choose a secret-storage or deployment policy. Node-specific findings are not generalized to Bun without separate evidence, and nothing here is an operational requirement or implementation instruction. Each claim stays with the loader, runtime, version, mode, and evidence type that supports it. The cited Node.js pages are the released v26.13.1 documentation; Node programmatic behavior is also pinned to tag `v24.18.0` and a bounded run on Node v24.18.0. Bun behavior is pinned to tag `bun-v1.3.14` (commit `0d9b296af33f2b851fcbf4df3e9ec89751734ba4`) and a bounded run on Bun 1.3.14, while Bun's documentation pages are rolling.

## Five Configuration Sources

Configuration may enter a process through environment variables, files, command-line arguments, or platform-specific mechanisms. These are different surfaces, not interchangeable spellings of "the environment":

- **Inherited environment variables.** `process.env` holds the variables set when the process started, and Node documents that it can be modified and expanded afterward ([Node.js v26.13.1 Environment Variables](https://nodejs.org/download/release/v26.13.1/docs/api/environment_variables.html)). A value inherited from the parent process or operating system is present before any application code runs. Its presence proves delivery through that route, not where the value originally came from.
- **Node's `--env-file` option.** Node reads the named file before application execution and makes its values available on `process.env`; `--env-file-if-exists` behaves the same but does not throw when the file is missing. File values, including `NODE_OPTIONS`, are parsed at startup ([Node.js v26.13.1 Command-line API](https://nodejs.org/download/release/v26.13.1/docs/api/cli.html)).
- **Node programmatic loading and parsing.** `process.loadEnvFile(path?)` loads a file into `process.env` during execution, defaults to `./.env`, and therefore cannot change startup options such as `NODE_OPTIONS` ([Node.js v26.13.1 Process API](https://nodejs.org/download/release/v26.13.1/docs/api/process.html#processloadenvfilepath)). `util.parseEnv(content)` parses raw `.env` text and returns an object without touching `process.env`; a repeated key keeps its last value in that object ([Node.js v26.13.1 Util API](https://nodejs.org/download/release/v26.13.1/docs/api/util.html#utilparseenvcontent)). The two calls are separate surfaces: one writes process state, the other returns a dictionary.
- **Bun's documented loading.** Bun automatically loads a set of `.env` files and also accepts explicit `--env-file` arguments. Invoked as `node`, it disables automatic loading to match Node while still honoring explicit files. Automatic loading is disabled by `--no-env-file`, by top-level `env = false` in `bunfig.toml`, or by `[env]` with `file = false`; explicit `--env-file` files still load in each case ([Bun environment variables](https://bun.com/docs/runtime/environment-variables)). Bun expands `$VAR` references inside environment files, so its parsing is not identical to Node's.
- **Application-level validation.** Parsing produces textual keys and values. Deciding that `"3000"` is an acceptable port, that `"false"` means disabled, or that `{ "hello": "world" }` is valid configuration is a separate application step. No loader on this page types, coerces, or validates those values for the application.

Keep secret delivery separate from secret storage. Sending a value through the environment or a file is a delivery choice; it does not establish file permissions, rotation, access control, or encryption. Environment variables are generally readable by the process and may also appear in logs, error output, process reports, or system dumps, as OWASP notes in its container secret-injection context ([OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)).

## Precedence, Per Loader And Surface

### Node CLI Environment Files

Node's released CLI reference states two rules for `--env-file`: a value already defined in the process environment takes precedence over the file's value, and multiple `--env-file` arguments are applied so that a later file overrides variables defined in an earlier file ([Node.js v26.13.1 Command-line API](https://nodejs.org/download/release/v26.13.1/docs/api/cli.html)). Combined, the documented CLI order is:

> inherited process value > later `--env-file` file > earlier `--env-file` file

`NODE_ENV` has no documented role in choosing `--env-file` files. Node loads only the files it is explicitly given and documents no automatic mode-file selection.

### Node Programmatic Loading And Parsing

The released v26.13.1 `process.loadEnvFile()` reference describes the load but does not state an overwrite rule. That omission is a documentation gap, not an unknown behavior: bounded execution on Node v24.18.0 and the maintainer records behind the documentation change establish the sequence ([Node.js PR #67276](https://github.com/nodejs/node/pull/67276); [Node.js issue #63027](https://github.com/nodejs/node/issues/63027)). The sequence-sensitive order is:

> inherited value present at start > first-applied `--env-file` source, with later CLI files overriding earlier CLI files but never overriding the inherited value > first `process.loadEnvFile()` call > later `process.loadEnvFile()` calls

Equivalently, once a key exists in `process.env`, neither a later `loadEnvFile()` call nor an earlier `--env-file` file overwrites it. At startup, CLI files are applied in argument order, so a later CLI file wins over an earlier one; after startup, `loadEnvFile()` only fills keys that are still absent, so the first programmatic call wins over later calls. `util.parseEnv()` never writes `process.env` at all, and its repeated-key rule applies only inside the object it returns.

### Bun Automatic And Explicit Loading

Bun's environment page documents automatic loading in increasing precedence: `.env`; the mode-specific `.env.production`, `.env.development`, or `.env.test`; `.env.local`; and the mode-local `.env.production.local`, `.env.development.local`, or `.env.test.local`. `.env.local` is not loaded when `NODE_ENV=test` ([Bun environment variables](https://bun.com/docs/runtime/environment-variables)). The rolling page does not state a complete order between those files and an inherited process value.

The pinned 1.3.14 source and a bounded Bun 1.3.14 run add a resolved but version-bounded order ([Bun `src/dotenv/env_loader.zig` at `bun-v1.3.14`](https://github.com/oven-sh/bun/blob/bun-v1.3.14/src/dotenv/env_loader.zig)):

> inherited process value > explicit `--env-file` files, which replace the default set and give a later argument higher priority > the automatic set, lowest to highest: `.env` < `.env.{mode}` < `.env.local`, skipped in test mode < `.env.{mode}.local`

Within the automatic set the first key set wins, so the mode-local file has the highest precedence and `.env` the lowest. An explicit `--env-file` replaces the default selection rather than adding to it, and later explicit arguments win over earlier ones. Treat all of this as the pinned 1.3.14 result, not a universal Bun rule: the published page is rolling and gives no complete inherited-vs-file order, and one release is not an every-version contract.

The mode selector is also version-bounded. Bun's pinned 1.3.14 source reads `BUN_ENV` first and then `NODE_ENV`; any other value selects development. A `BUN_ENV` or `NODE_ENV` defined only inside `.env` is loaded as a value but does not retroactively choose the mode file, because the selector is taken from the process environment at load time ([Bun environment variables](https://bun.com/docs/runtime/environment-variables); [Bun `src/dotenv/env_loader.zig` at `bun-v1.3.14`](https://github.com/oven-sh/bun/blob/bun-v1.3.14/src/dotenv/env_loader.zig)). The pinned source and the bounded Bun 1.3.14 run establish `BUN_ENV`-over-`NODE_ENV` precedence for `bun run` mode selection; the inspected evidence does not establish how a set `BUN_ENV` interacts with `bun test`.

### The `bun test` Route And `NODE_ENV`

`bun test` is a separate command route from `bun run`. The current Bun test-behavior page says the command sets `NODE_ENV` to `"test"` unless it is already set in the environment or in `.env` files ([Bun test runtime behavior](https://bun.com/docs/test/runtime-behavior)). On Bun 1.3.14, the pinned source, the repository test's expectations, and an isolated observation of that route settle the tested case differently ([Bun `test/cli/run/env.test.ts` at `bun-v1.3.14`](https://github.com/oven-sh/bun/blob/bun-v1.3.14/test/cli/run/env.test.ts)):

- With the shell value unset and `NODE_ENV=staging` in `.env`, `bun test` reports `NODE_ENV=test`: the file value is overwritten in this route.
- With `NODE_ENV=staging` in the shell, `bun test` reports `staging`: a pre-existing process value remains.
- In test mode, `.env.test.local`, `.env.test`, and `.env` load, while `.env.local` does not.

A `NODE_ENV` value loaded from a file does not replace the test runner's default in this route, while a value present in the starting process environment does.

State the command route and the starting environment whenever describing this behavior. The result is specific to `bun test` on 1.3.14 and is not universalized to every Bun invocation or environment-loading route. The publisher page sentence is inaccurate for that release, and maintainer records report that a file value won through Bun 1.0.17 while the default has won from 1.0.18 ([Bun PR #48095](https://github.com/oven-sh/bun/pull/48095)).

### No Universal Precedence Order

No universal order across inherited values, Node CLI files, Node programmatic calls, Bun automatic loading, and third-party loaders follows from these sources. The documented and observed rules are per loader, per surface, and per version, and the Bun page itself leaves the inherited-vs-file comparison incomplete. No security policy, compliance rule, or organization-wide configuration standard is established here.

## Parsing, Validation, And Presence

Node documents that parsed `.env` values are strings: `0`, `true`, and `{ "hello": "world" }` become `"0"`, `"true"`, and `"{ \"hello\": \"world\" }"`, not a number, a boolean, and an object ([Node.js v26.13.1 Environment Variables](https://nodejs.org/download/release/v26.13.1/docs/api/environment_variables.html)). Parsing therefore establishes a string-valued presence, not a type or a valid meaning. Presence and validity are separate facts: a present key can hold `"false"` and still be present, while an absent key has no value at all.

The common mistake is to pass the raw string to a truthiness check. The string `"false"` is truthy, so a truthiness test reads a disabled setting as enabled:

```ts
const misread = Boolean(process.env.FEATURE_ENABLED); // "false" becomes true.
```

If the application's documented convention treats only the literal `"true"` as enabled, an explicit parser should say so and report presence or validation outcome without printing the raw value:

```ts
interface BooleanSettingOutcome {
  present: boolean;
  valid: boolean;
  enabled?: boolean;
}

function parseBooleanSetting(raw: string | undefined): BooleanSettingOutcome {
  if (raw === undefined) return { present: false, valid: false };
  if (raw === "true") return { present: true, valid: true, enabled: true };
  if (raw === "false") return { present: true, valid: true, enabled: false };
  return { present: true, valid: false }; // Present, but not a recognized boolean.
}

const outcome = parseBooleanSetting(process.env.FEATURE_ENABLED);
console.info({
  featureSettingPresent: outcome.present,
  featureSettingValid: outcome.valid,
  enabled: outcome.enabled,
});
```

That contrast is illustrative, not a universal setting convention. The application's own accepted values decide what `"false"`, `"0"`, or an empty string mean. Report presence or the validation outcome rather than logging the raw value, which may be sensitive. The type of `process.env.FEATURE_ENABLED` depends on the project's Node type definitions and compiler settings; verify the installed declarations instead of assuming a particular `string | undefined` or literal type.

## Exposure, Trust, And Diagnostics

Avoid exposing credentials or sensitive values in logs, errors, process reports, or diagnostics. Node's CLI documents `--report-exclude-env` to omit `environmentVariables` data from a diagnostic report, and `--trace-env` to print environment-variable access names rather than their values ([Node.js v26.13.1 Command-line API](https://nodejs.org/download/release/v26.13.1/docs/api/cli.html)). Those are configuration-exposure controls on one diagnostic surface, not a complete secrecy guarantee: report content and exclusion options are runtime-specific, a report is a runtime snapshot rather than a telemetry-export pipeline, and other output paths may still reveal values.

Trust is a separate question from delivery, and untrusted input is distinct from trusted code. Node's CLI warns that a user-provided JSON configuration file passed to `--config-file` is not sanitized or validated, and advises against using an untrusted configuration file. That warning is specific to that Node CLI surface; it does not establish that `.env` files are validated, and it states no equivalent Bun rule. A dotenv value is neither automatically safe nor automatically unsafe. Its trust depends on who can write the file or environment, how it reaches the process, and what the application validates afterward.

Node's permission model restricts selected runtime capabilities, but it is not a complete sandbox for arbitrary code or dependencies ([Node.js v26.13.1 Permission model](https://nodejs.org/download/release/v26.13.1/docs/api/permissions.html)). Third-party package execution remains a trust boundary, and the permission model is not a substitute for threat analysis. No organization-wide security policy, compliance rule, or universal hardening checklist follows from this page.

Third-party loaders are separate products, not aliases for the built-ins. `dotenv@18.0.9` keeps existing `process.env` values by default and, for a `path` array, keeps the first file's value unless override is enabled; `dotenv-cli` (`-e`, `-c`) and `dotenvx` (`-f`, `--overload`) are distinct packages with their own flags ([dotenv v18.0.9 README](https://github.com/motdotla/dotenv/tree/v18.0.9); [dotenv-cli README](https://github.com/entropitor/dotenv-cli); [dotenvx README](https://github.com/dotenvx/dotenvx)). Their default multi-file direction is the opposite of Node's and Bun's `--env-file` rule, and an override flag does not transfer between products. `dotenv.parse` returns an object without writing `process.env`, like Node's `util.parseEnv`.

## Diagnose A Missing Or Misread Setting

When a service behaves as if an environment-backed option is absent or has an unexpected value, first ask how the process received configuration, then whether a loader ran. A file's presence is not evidence that it was loaded, and a loader's presence is not evidence that its value won.

1. Record the exact command, runtime and version, working directory, launcher, and parent environment that started the process. These facts identify the inherited surface and any wrapper that could have injected values.
2. Identify the loading surface: an inherited value, a Node `--env-file` argument, a programmatic `process.loadEnvFile()` call, a `util.parseEnv()` result the application read, or Bun's automatic files. Record when each applies, because startup loading and execution-time loading are different moments.
3. Check whether the key exists before checking its meaning. An absent key and a present but unrecognized string are different findings: the first can come from a loader that did not run or a lower-precedence source that lost, while the second is a validation outcome.
4. Compare the value against the application's accepted values and report presence or the validation outcome, not the raw value. If the application documented only the literal `"true"` as enabled, a present `"false"` is disabled rather than missing.
5. If the expected loader or setting source cannot be established, say so. The observed environment alone does not identify why a value is missing, and neither a file's presence nor a documented default proves which source won.

Node's v26.13.1 documentation supports the loader surfaces in this sequence, but the programmatic overwrite rule comes from the bounded execution and maintainer records described above rather than from the released API sentence. Bun's automatic and explicit loading is documented separately, and its test route has the version-bounded `NODE_ENV` behavior described above. Do not substitute one runtime's loader rules for the other.

## Limits And Version Boundaries

- Node's released v26.13.1 documentation documents `--env-file`, `process.loadEnvFile()`, and `util.parseEnv()`, and states that parsed values are strings. The programmatic overwrite and sequence behavior is additionally established by a Node v24.18.0 run and maintainer records; the released API page's silence is a documentation gap, not a behavior unknown.
- Bun's loading is documented separately on rolling pages that expose no release version. The pinned source, repository test, and runtime observation bound the claims to Bun 1.3.14 (tag `bun-v1.3.14`), and the `BUN_ENV`-over-`NODE_ENV` selector result is bounded to `bun run` mode selection. No first stable release is claimed for any behavior.
- `process.env` typing depends on the project's Node type definitions and compiler configuration and must be verified. A checker's view of a setting is not the loader's behavior.
- Third-party loader behavior is bounded to the named package versions and flags; an override option or multi-file direction does not transfer between products.
- No universal precedence order or security policy is stated. No loader on this page is tested against an uninspected project, and no compatibility promise follows for another Node, Bun, or dotenv version.
- Nothing here selects, prescribes, or assumes Vite; an incidental dependency edge is neither evidence of direct selection nor proof of its absence. No step on this page forms an implicit pipeline.
- The repository's deterministic utilities under `scripts/node/` have their own Bun and repository conventions. Those conventions are not ordinary project defaults.

## Ownership And Routing

This page is passive interpretation. Configuration changes that alter application behavior go to the production owner, `node-project-writer -> reference/change-design-and-validation.md`. Dependency, lockfile, or environment-selection changes go to `node-project-dependencies -> reference/evaluation-and-environment-changes.md`. Secret or trust decisions remain with the requester or organization; no approval or policy decision follows from this page.

Runtime execution, module resolution, and the mixed manager-and-runtime reading are covered in [Runtime And Project Structure](runtime-and-project-structure.md). Manager, lockfile, workspace, and invocation evidence is covered in [Manager, Workspace, And Invocation Evidence](manager-workspaces-and-invocation.md). Diagnostic report content, trace output, and telemetry-export boundaries are covered in [Diagnostics And Telemetry](diagnostics-and-telemetry.md); this page names only the configuration-exposure controls needed to avoid leaking values. Concurrency, cancellation, and lifecycle behavior is covered in [Concurrency And Lifecycle](concurrency-and-lifecycle.md); no configuration-loading rule here establishes parallel execution, cancellation, or shutdown behavior.
