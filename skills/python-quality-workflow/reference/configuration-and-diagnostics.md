# Configuration And Diagnostics

## Establish What A Check Actually Analyzes

A tool name and exit code are not enough to interpret a run. Record the binary
version, effective configuration and overrides, working directory, target paths,
Python/platform assumptions, dependency/import environment, selected rules or mode,
and suppressions. Compare local and CI results only after comparing these inputs.
A clean result can reflect a narrower file set or different environment rather than
the absence of the original problem.

Before interpreting a surprising result, capture the execution context as data rather
than guessing from a shell prompt. For example, these are **documentation-only,
check-oriented probes** for a project whose existing commands invoke the named tools;
adapt them to its manager and configured entry points:

```sh
pwd
python --version
ruff --version
pyright --version
pytest --version
coverage --version
```

Record the interpreter actually selected by the project command as well as the shell's
`python`; wrappers and CI may select different environments. Then record the exact
working directory and target paths, selected config file, tool-specific overrides,
Python/platform target, dependency/stub environment, and local/CI invocation. A version
probe does not prove which executable a wrapper later runs, so retain the actual command
and its output. If a tool has no version/config inspection mode in the installed
version, say that the value was not independently confirmed rather than infer it.

Preserve current project settings first. For a new configuration, distinguish a tool's
documented defaults from a deliberate project choice; neither automatically creates
enterprise policy. Explicitly load `python-project-reference` and read
`python-project-reference -> reference/project-baseline-and-adoption.md` for the
shared adoption proposal rather than importing a whole baseline into each task.

## Ruff: Selection, Formatting, And Writes Are Separate

Ruff's linter and formatter have distinct effects:

- `ruff check` diagnoses enabled lint rules, subject to the effective settings.
- `ruff check --fix` writes available fixes. Safe fixes are the normal default;
  unsafe fixes require opt-in and may change behavior or comments. Not every finding
  has a fix.
- `ruff format` writes formatting; `ruff format --check` detects formatting changes
  without rewriting source.
- Import sorting belongs to the selected isort-derived `I` lint family. Running the
  formatter does not select or apply it.

These distinctions are documented for [Ruff 0.17.3 linting](https://github.com/astral-sh/ruff/blob/0.17.3/docs/linter.md)
and [formatting](https://github.com/astral-sh/ruff/blob/0.17.3/docs/formatter.md).
The formatter aims at Black compatibility but has known deviations and limited style
options; some lint/isort settings conflict with it. A formatting pass is conformity to
the selected formatter, not a design or runtime-correctness score.

For an unconfigured hypothetical Python 3.11 project that explicitly chooses import
sorting, a small configuration could be:

```toml
[tool.ruff]
target-version = "py311"
preview = false

[tool.ruff.lint]
select = ["E", "F", "I"]
```

The Python target and `I` selection are choices in this example, not recommendations
for every project. Selecting `ALL` can enable newly added rules after an upgrade;
preview is a separate opt-in, not an automatic consequence of `ALL`. Even stable rules
and formatting can change across version upgrades, so an explicit list is a controlled
surface, not a frozen implementation
([Ruff preview](https://github.com/astral-sh/ruff/blob/0.17.3/docs/preview.md),
[version policy](https://docs.astral.sh/ruff/versioning/)). Security-oriented rules can
favor false positives; selecting every security, pedantic, or restriction category is
not equivalent to a security audit or a generally suitable baseline
([rule-selection guidance](https://docs.astral.sh/ruff/linter/)).

## Worked Diagnosis: An Excluded File Still Reports

Assume a project excludes generated code, yet a local Ruff invocation names
`generated/client.py` directly and reports findings. First inspect the exact invocation
and selected config: in Ruff 0.17.3, a directly passed file can be analyzed despite an
exclude unless `force-exclude` is enabled. A CI run that discovers files from a directory
may therefore see a different scope without either run having a broken rule engine
([Ruff configuration and file discovery](https://github.com/astral-sh/ruff/blob/0.17.3/docs/configuration.md)).

Also inspect config hierarchy. Ruff normally uses the closest applicable config rather
than merging every ancestor; inheritance must be expressed through the supported
configuration mechanism. CLI values override settings. Python target inference from
`requires-python` applies only under its documented discovery conditions, so a
directly supplied config or a different working directory can change the result.

Do not “fix” this discrepancy by suppressing the generated file or editing it. Report
which invocation/config/path-selection difference explains the observations. Change
the exclusion or invocation only if that quality-configuration outcome is requested
and authorized. Review the resulting analyzed file set, not just whether the count fell.

## Pyright: Mode Is Only One Part Of The Analysis

Pyright 1.1.414 supports `off`, `basic`, `standard`, and `strict`; `standard` is the
documented default. Per-diagnostic overrides can change effective behavior. `off`
retains syntax/semantic diagnostics; strict enables most checks, not every possible
project policy. Strict paths apply to included files
([configuration](https://github.com/microsoft/pyright/blob/1.1.414/docs/configuration.md),
[incremental typing](https://github.com/microsoft/pyright/blob/1.1.414/docs/getting-started.md)).

```json
{
  "include": ["src/reporting"],
  "exclude": ["src/reporting/generated"],
  "pythonVersion": "3.11",
  "typeCheckingMode": "standard",
  "strict": ["src/reporting/new_rules"]
}
```

This hypothetical configuration selects a source scope and stricter new-module scope;
it does not specify every dependency, interpreter, platform, or import path. If both
`pyrightconfig.json` and `[tool.pyright]` exist, the JSON file takes precedence. Paths
are config-relative. Do not interpret an edited TOML setting as effective until the
selected config is known.

Pyright exclusion differs from a hard runtime boundary: an excluded file can still be
analyzed when included code imports it. For an unexpected generated-module diagnostic,
trace the import edge rather than assuming the Ruff explanation also applies.
Imports depend on workspace code, extra paths, stubs, typed packages, typeshed, and the
selected environment. Executable editable-install import hooks cannot be run by the
analyzer, so runtime import success need not imply Pyright resolution success
([Pyright 1.1.414 import resolution](https://github.com/microsoft/pyright/blob/1.1.414/docs/import-resolution.md)).

When local and CI import diagnostics differ, compare interpreter/dependency/stub
availability before widening ignores or tightening the mode. A configured venv is
not mandatory if local code and stubs resolve all imports, but an unresolved import
environment makes an apparent clean or noisy result hard to interpret.

## Tighten An Established Project Without Hiding Debt

Capture existing diagnostics with the current versions, rules, target, paths,
environment, and suppressions. Preserve the enforced profile unless a configuration
change is requested. A bounded ratchet can distinguish existing debt from newly
introduced findings in changed scope; adding a rule changes the measurement and needs
its own baseline rather than being called a regression in old code.

Ruff documents staged rule additions and `RUF100` for unused suppressions. Its
`--add-noqa` mechanism writes comments to source: it is a migration/edit, not a diagnostic
shortcut this operation may use. Likewise, repairing an unused suppression requires
the appropriate source/test owner, even when the quality report identifies it
([Ruff incremental adoption](https://docs.astral.sh/ruff/tutorial/),
[suppression mechanics](https://github.com/astral-sh/ruff/blob/0.17.3/docs/linter.md)).

Pyright's staged guidance supports explicit include paths, selected diagnostics, and
strictness for chosen files/directories. It does not justify a blanket strict migration
or removal of all existing exceptions. Separate the authorized configuration decision
from source work needed to satisfy it.

## Interpret Outputs As Scoped Measurements

Ruff can report counts by violated rule and expose files/settings; those counts are
not normalized defect rates. Pyright JSON includes version/time, diagnostics, analyzed
file counts, severity totals, and elapsed time. Its `--stats` reports performance,
not software quality ([Ruff CLI](https://docs.astral.sh/ruff/configuration/#command-line-interface),
[Pyright 1.1.414 CLI](https://github.com/microsoft/pyright/blob/1.1.414/docs/command-line.md)).

For an installed `py.typed` library, Pyright's `--verifytypes` is a separate public-symbol
type-completeness measure. Public/private conventions and `__all__` handling determine
the interface denominator, and `--ignoreexternal` changes treatment of unknown external
types. It is not general application annotation coverage or runtime API validation
([typed-library guidance](https://github.com/microsoft/pyright/blob/1.1.414/docs/typed-libraries.md)).

A clean static check does not run the application; Python does not enforce annotations
as runtime validation ([Python typing](https://docs.python.org/3/library/typing.html)).
Report invalid config, tool failure, diagnostics, skipped checks, and unavailable tools
as distinct outcomes instead of flattening all non-passes into a defect count.

## Interpret Test And Coverage Reports Without Remediation

For requested test checks, record actual collected targets, deselections, skips, and
fixture setup failures. A test that never reached its action/assertion does not provide
that behavior evidence. A passing case supports its assertion, not all possible oracles
([pytest anatomy](https://docs.pytest.org/en/stable/explanation/anatomy.html),
[pytest 9.2.0 fixtures](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/how-to/fixtures.rst)).

For coverage, report source universe, test-file inclusion, report filters, exclusions,
line/branch mode, threshold, artifact, versions, and relevant process/data aggregation.
For example, changing a report from production-only to production-plus-tests can raise
its total even though no production path gained a test. Adding eligible unexecuted
modules or branch opportunities can lower it without any deleted test. Neither is a
like-for-like trend ([coverage.py 7.17.2 source](https://coverage.readthedocs.io/en/7.17.2/source.html),
[branches](https://coverage.readthedocs.io/en/7.17.2/branch.html),
[exclusions](https://coverage.readthedocs.io/en/7.17.2/excluding.html)).

Coverage.py recommends including tests; a production-first report is a different
purpose choice, not its mandated denominator. Configured `fail_under` and precision
control the gate; no universal percentage follows. Coverage.py 7.17.1 fixed decimal
threshold comparison, and 7.17.2 fixed combining issues, so a changed exit result can
also require a version/data investigation
([configuration](https://coverage.readthedocs.io/en/7.17.2/config.html),
[change history](https://coverage.readthedocs.io/en/7.17.2/changes.html)).

If pytest-cov is present, inspect plugin overrides as well as coverage configuration:
`--cov=...` overrides source, `--cov-branch` overrides branch, and the plugin controls
parallel handling. The inspected pytest-cov 7.1.0 guidance delegates subprocess
measurement to coverage.py after removal of its own support in 7.0. Missing worker or
subprocess data is not evidence that the associated code is untested
([plugin configuration](https://pytest-cov.readthedocs.io/en/latest/config.html),
[subprocess support](https://pytest-cov.readthedocs.io/en/latest/subprocess-support.html),
[worker aggregation](https://pytest-cov.readthedocs.io/en/latest/xdist.html)).

## Bound Effects And Further Reading

Inspect effective write settings before invoking even a normally diagnostic command.
Do not autofix, format source, generate suppressions, or edit tests to repair findings.
Caches, coverage data, and report artifacts are still writes; authorize their paths and
destinations separately from source non-writing mode. Keep dependency installs/lock
changes and unrelated CI changes outside incidental quality work.

### Separate a report run from a configuration change

An authorized check-only request means preserve the checked-in quality configuration
and report what its configured commands do. Do not turn that into a new lint profile,
mode, path set, coverage denominator, threshold, or CI gate. A proposed configuration
change is a distinct outcome: identify the exact quality setting and file, explain its
scope and compatibility effect, obtain authorization for that change, review the diff,
and validate the setting with the target tool if available. Neither outcome authorizes
editing production code, tests, fixtures, helpers, or suppressions to make results pass.

The following examples are **documentation-only** and illustrate different questions;
they are not commands run against a target project or a universal sequence:

```sh
# Inspect scope/results without requesting Ruff fixes or formatting writes.
ruff check --show-files src tests
ruff check --statistics src tests
ruff format --check src tests

# Inspect pytest collection without executing tests.
pytest --collect-only -q

# A test/coverage run measures execution but may write coverage data and reports.
# Use only when those destinations and effects are authorized.
coverage run -m pytest
coverage report -m
```

`pytest --collect-only` is not a test pass. A normal pytest/coverage run can execute
project code, fixtures, plugins, and external integrations; “diagnostic” does not mean
side-effect-free. Inspect pytest options and plugin configuration for `addopts`,
`--cov`, `--cov-config`, branch mode, parallel/subprocess data, and report destinations.
Likewise, Ruff's check commands may create or update tool caches even when they do not
rewrite source. State the observed write status and destinations (or that they were not
verified); do not call a command wholly non-writing merely because it omits `--fix`.

Coverage interpretation should name the measured source universe and whether tests are
included, test files actually collected, include/omit and report filters, line versus
branch mode, exclusions, configured threshold/precision, data aggregation, report
artifact, and tool/plugin versions. A changed percentage alone is not a trend: adding
eligible unexecuted files, changing branch opportunities, or changing test inclusion
changes the denominator. A threshold is a configured gate, not proof that the percentage
is suitable or that assertions detect defects.

For deeper domain mechanics, explicitly load `python-project-reference` and read
`python-project-reference -> reference/static-quality.md` or
`python-project-reference -> reference/testing-and-coverage.md` as needed. Preserve
target-project versions/configuration rather than treating the examples here as tool
selection instructions. The live Ruff, pytest-cov, and stable pytest links reflect
historical November 2026 inspections; they are not fresh fetches or release-frozen
documents. The tagged Ruff 0.17.3, Pyright 1.1.414, pytest 9.2.0, and coverage.py
7.17.2 links give narrower scopes, not evidence of a target installation.
