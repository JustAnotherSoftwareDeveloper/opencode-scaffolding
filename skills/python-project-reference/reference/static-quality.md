# Static Quality

## Interpret The Effective Analysis, Not The Tool Name

Ruff lint, autofix, formatting, and import sorting are separate functions. Ruff 0.17.3
documents that `ruff format --check` checks without rewriting and that formatting does
not sort imports. Import sorting is an explicit lint-rule choice such as `I`; `ruff
check --fix` and `ruff format` can write eligible changes. A clean result says only that
the selected tool/configuration found no reported issue in its effective scope. It
does not establish runtime correctness. (Dossier C05-C06; [Ruff 0.17.3 linter](https://github.com/astral-sh/ruff/blob/0.17.3/docs/linter.md), [formatter](https://github.com/astral-sh/ruff/blob/0.17.3/docs/formatter.md).)

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
trade-off, not a measured quality result. (C06, C24; [Ruff 0.17.3 configuration](https://github.com/astral-sh/ruff/blob/0.17.3/docs/configuration.md), [preview behavior](https://github.com/astral-sh/ruff/blob/0.17.3/docs/preview.md).)

Pyright has a different resolution model. In 1.1.414, `pyrightconfig.json` takes
precedence over `[tool.pyright]` when both exist; config paths are resolved relative to
the chosen config. `include`, Python/platform target, execution environment, interpreter,
dependencies, stubs, and imports all affect diagnostics. An excluded module can still
be analyzed when included code imports it. Mode names do not summarize those inputs.
(C07, C24; [Pyright 1.1.414 configuration](https://github.com/microsoft/pyright/blob/1.1.414/docs/configuration.md) and [import resolution](https://github.com/microsoft/pyright/blob/1.1.414/docs/import-resolution.md).)

```json
{
  "include": ["src/acme_metrics"],
  "pythonVersion": "3.11",
  "typeCheckingMode": "standard"
}
```

This Pyright fragment assumes a project whose declared minimum is Python 3.11. It does
not specify an interpreter, platform, installed dependency set, or every import path;
those remain part of the effective analysis.

## Troubleshoot Unexpected Or Missing Diagnostics

When an excluded file still reports, first distinguish Ruff from Pyright and inspect
the exact config file, invocation path, CLI overrides, and imported-file relationships.
For Ruff, check whether a file was passed directly and whether `force-exclude` is set.
For Pyright, check config precedence, config-relative `include`/`exclude`, the import
that reaches the file, target version, interpreter, and available stubs. C24 supports
these mechanics for Ruff 0.17.3 and Pyright 1.1.414; it does not establish the settings
of a target repository.

For a new project selecting these tools, explicit paths and a target matching declared
support make the checker scope easier to interpret. Strictness and rule coverage are
choices, not mandates. For a library that advertises typed support, Pyright's
[`--verifytypes` feature](https://github.com/microsoft/pyright/blob/1.1.414/docs/typed-libraries.md)
measures its detected public typed interface; it is not an application
annotation-coverage score. Its result depends on the interface Pyright identifies and
how it treats unknown external types.

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
