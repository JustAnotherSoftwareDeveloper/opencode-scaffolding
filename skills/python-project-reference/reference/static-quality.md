# Static Quality

## Interpret The Effective Analysis, Not The Tool Name

Ruff lint, autofix, formatting, and import sorting are separate functions. Ruff 0.17.3
documents that `ruff format --check` checks without rewriting and that formatting does
not sort imports. Import sorting is an explicit lint-rule choice such as `I`; `ruff
check --fix` and `ruff format` can write eligible changes. A clean result says only that
the selected tool/configuration found no reported issue in its effective scope. It
does not establish runtime correctness. ([Ruff 0.17.3 linter](https://github.com/astral-sh/ruff/blob/0.17.3/docs/linter.md), [formatter](https://github.com/astral-sh/ruff/blob/0.17.3/docs/formatter.md).)

One possible starting profile for a new project is deliberately explicit:

```toml
[tool.ruff]
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I"]
```

Assumption: this hypothetical package supports Python 3.11 or newer and has chosen
import sorting. The selection is not a universal quality profile. Ruff 0.17.3 uses the
closest config for a file; it does not merge parent configs unless the child extends
them. CLI values override config. A file passed directly is still analyzed when it
matches `exclude` unless `force-exclude` is enabled. Thus a generated file reported
only when named directly can be explained by invocation scope rather than a broken
exclude pattern. Ruff also warns that selecting `ALL` can add rules after upgrades;
preview lint and formatter behavior are separate opt-in choices. Prefer an explicit
rule surface when upgrades should not silently expand the profile. This is a stability
trade-off, not a measured quality result. ([Ruff 0.17.3 configuration](https://github.com/astral-sh/ruff/blob/0.17.3/docs/configuration.md), [preview behavior](https://github.com/astral-sh/ruff/blob/0.17.3/docs/preview.md).)

Pyright has a different resolution model. In 1.1.414, `pyrightconfig.json` takes
precedence over `[tool.pyright]` when both exist; config paths are resolved relative to
the chosen config. `include`, Python/platform target, execution environment, interpreter,
dependencies, stubs, and imports all affect diagnostics. An excluded module can still
be analyzed when included code imports it. Mode names do not summarize those inputs.
([Pyright 1.1.414 configuration](https://github.com/microsoft/pyright/blob/1.1.414/docs/configuration.md) and [import resolution](https://github.com/microsoft/pyright/blob/1.1.414/docs/import-resolution.md).)

```json
{
  "include": ["src/acme_metrics"],
  "strict": ["src/acme_metrics/core"],
  "pythonVersion": "3.11",
  "typeCheckingMode": "standard"
}
```

This Pyright fragment assumes a project whose declared minimum is Python 3.11. It
checks the included package in `standard` mode and opts the included `core` subtree
into strict checking. The `strict` list does not include otherwise omitted paths.
Pyright 1.1.414 also supports `# pyright: strict` for a file and per-diagnostic
overrides, so strictness can be adopted by a bounded path rather than changing every
module at once. `off` still reports syntax/semantic errors; `strict` is not a promise
that every conceivable rule is enabled. The fragment leaves interpreter, platform,
installed dependencies, and additional import paths unspecified. ([Pyright 1.1.414
gradual adoption](https://github.com/microsoft/pyright/blob/1.1.414/docs/getting-started.md).)

## Inspect Files, Settings, And Results

For the illustrative `src/acme_metrics` package and external `tests/` directory, these
Ruff invocations answer different diagnostic questions without applying source fixes:

```sh
ruff check --show-settings src/acme_metrics/api.py
ruff check --show-files src tests
ruff check --statistics src tests
ruff check --output-format json src tests
ruff format --check src tests
```

`--show-settings` exposes resolved settings for a representative file; repeat for a
file under another config boundary rather than assuming one project-wide result.
`--show-files` lists discovered input files. `--statistics` counts reported violations
by rule, while JSON preserves individual diagnostic locations/codes for tooling.
Neither counts suppressed findings or represents a normalized defect rate. The
inspection/output options are documented in Ruff's mutable [CLI reference](https://docs.astral.sh/ruff/configuration/#command-line-interface),
recorded in the November 2026 research; the version-tagged configuration behavior
above does not freeze that live CLI reference to every future release.

Pyright 1.1.414 has its own result format:

```sh
pyright --project pyrightconfig.json --outputjson
pyright --project pyrightconfig.json --stats
```

JSON includes tool version, individual diagnostics, and summary fields such as files
analyzed and error/warning/information counts. `--stats` reports analysis performance,
not application annotation coverage. Inspect config/import scope alongside the result;
positional file arguments can override configured includes, so changing the invocation
can change what is checked. Preserve the exit status as well as the rendered report:
invalid configuration or a fatal tool error is not a clean analysis. ([Pyright
1.1.414 CLI and JSON schema](https://github.com/microsoft/pyright/blob/1.1.414/docs/command-line.md).)

## Troubleshoot Unexpected Or Missing Diagnostics

When an excluded file still reports, first distinguish Ruff from Pyright and inspect
the exact config file, invocation path, CLI overrides, and imported-file relationships.
For Ruff, check whether a file was passed directly and whether `force-exclude` is set.
For Pyright, check config precedence, config-relative `include`/`exclude`, the import
that reaches the file, target version, interpreter, and available stubs. These mechanics
describe Ruff 0.17.3 and Pyright 1.1.414, not the settings of a target repository.

Runtime import success does not settle checker import success. Pyright cannot execute
editable-install import hooks to discover files. If the runtime finds a package only
through such a hook, inspect the backend's editable-install mechanism and the
checker's source/stub paths before suppressing an unresolved import. A path-based
editable setup or regular installation can expose a different boundary; it is not a
reason to add arbitrary machine-specific paths to shared configuration. The tagged
import-resolution guide above describes this limitation.

For a new project selecting these tools, explicit paths and a target matching declared
support make the checker scope easier to interpret. Strictness and rule coverage are
choices, not mandates. For a library that advertises typed support, Pyright's
[`--verifytypes` feature](https://github.com/microsoft/pyright/blob/1.1.414/docs/typed-libraries.md)
measures its detected public typed interface; it is not an application
annotation-coverage score. Its result depends on the interface Pyright identifies and
how it treats unknown external types.

## Separate Fix Safety From Suppression Maintenance

Ruff documents safe fixes as the default for `ruff check --fix`; unsafe fixes require
explicit opt-in and can change runtime behavior or remove comments. Fix availability
and safety are rule-specific. A preview of eligible changes can be useful before
authorizing writes:

```sh
ruff check --diff src tests
```

`--diff` shows proposed changes without writing them; `--fix` writes eligible changes,
and adding `--unsafe-fixes` expands the allowed transformations. Review unsafe changes
as behavior changes, not just formatting. Rule-specific safety overrides can also
alter applicability, so the effective configuration matters even for a “safe” run.
Formatter/lint compatibility matters too: selected lint/isort options can conflict
with formatting; where both write, lint fixes conventionally precede formatting.
([Ruff fix safety](https://docs.astral.sh/ruff/linter/#fix-safety) and
[formatter conflicts](https://docs.astral.sh/ruff/formatter/#conflicting-lint-rules),
mutable publisher guidance recorded in the November 2026 research.)

Suppression maintenance answers a separate question. A narrow check such as
`ruff check --extend-select RUF100 src tests` can flag unused `noqa` directives;
review whether the rule disappeared, the code changed, or the suppression is stale.
`--add-noqa` instead **writes** suppressions for current findings when adopting new
rules. It is a migration tool, not a diagnostic baseline command. Keeping a rule
suppressed, fixing it, and excluding a path change different parts of the check
contract. ([Ruff unused suppressions](https://docs.astral.sh/ruff/linter/#detecting-unused-suppression-comments)
and [incremental adoption](https://docs.astral.sh/ruff/tutorial/).)

## Preserve Existing Tool Contracts

In an established project, retain effective configs, tool versions, targets, paths,
suppressions, formatter, and CI behavior unless the requested outcome justifies a
bounded change. Compare diagnostics only when versions, settings, paths, and import
environment are comparable or disclosed. Avoid applying fixes or reformatting files
solely to match a proposed profile.

The cited Ruff documentation is pinned to 0.17.3 and Pyright to 1.1.414. These versions
are evidence scopes, not target-project versions. Check the project's actual binary and
configuration before relying on version-specific behavior. General source conventions
belong to `python-source-style-guide -> reference/python-source-style-guide.md` when
that guide is explicitly loaded.

## Related Domains

- Runtime support and project roots belong to [Project Context and Layout](project-context-and-layout.md).
- Test behavior and coverage reports belong to [Testing and Coverage](testing-and-coverage.md).
- Dependency resolution and checker environments belong to [Environment and Dependencies](environment-and-dependencies.md).
