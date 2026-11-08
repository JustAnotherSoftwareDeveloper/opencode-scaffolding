# Environment And Dependencies

## Separate The Environment Coordinates

Do not treat a supported Python range, a selected interpreter, dependency declarations,
a virtual environment, a lock, and installed packages as interchangeable facts.
`requires-python` expresses declared compatibility intent; one selected interpreter is
one environment. A Python package lock does not lock the OS image, compiler, system
libraries, or interpreter installation. A sync changes installed state; it does not
replace the source declaration or lock.

Dependency categories have different consumers:

```toml
[project]
dependencies = ["urllib3"]

[project.optional-dependencies]
postgres = ["psycopg"]

[dependency-groups]
test = ["pytest"]
lint = ["ruff"]
dev = [{include-group = "test"}, {include-group = "lint"}]
```

Here `urllib3` is a runtime requirement, `postgres` is a published optional feature,
and `dev` is for development/task tools. PyPA specifies that dependency groups are not
emitted as package metadata; group-install commands are manager-specific. Names and
dependencies are illustrative and claim no compatibility result. The `dev` group
includes the test/lint groups; it is not an extra consumers can request from an
installed wheel. ([PyPA metadata specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
and [dependency groups specification](https://packaging.python.org/en/latest/specifications/dependency-groups/).)

## Read Lock Failures Precisely

For uv 0.13.5, a project invocation normally locks and syncs. `--locked` requires the
lock to be current and errors rather than updating when project metadata makes it
stale. `--frozen` uses the existing lock without checking whether it matches current
metadata. They express different conditions:

```sh
uv run --locked pytest
uv run --frozen pytest
```

These commands illustrate the distinction only; neither was run against a project.
If `--locked` reports staleness, inspect the metadata/lock mismatch. A successful
`--frozen` invocation does not establish freshness because it skips that check. Sync
also installs a selected subset of the resolution; that installed environment is not
the whole runtime image. ([uv 0.13.5 locking and syncing](https://github.com/astral-sh/uv/blob/0.13.5/docs/concepts/projects/sync.md).)

## Distinguish Selection, Exactness, And Upgrades

The recorded uv [sync documentation](https://docs.astral.sh/uv/concepts/projects/sync/)
distinguishes installed-set cleanup from lock freshness. `uv sync` is exact by
default: it removes extraneous packages not needed by the selected dependency set.
`uv run` syncs inexactly by default, retaining extraneous installed packages unless
they conflict with requirements. Thus a successful developer `uv run` can coexist
with tools left over from an earlier install; it does not prove that only declared
packages were available. `uv sync --inexact` deliberately changes the cleanup policy.

Groups and extras choose the installed subset, not independent resolutions. In uv's
documented project model, `dev` is a default group (configurable through
`tool.uv.default-groups`), whereas extras are not installed by default. For the
declarations above, the following examples have different intended environments:

```sh
uv sync --locked
uv sync --locked --no-default-groups --group test
uv sync --locked --no-default-groups --extra postgres
```

With the default group configuration, the first includes test/lint tools via `dev`;
the second selects runtime plus `test`, and the third runtime plus the `postgres`
extra. These syncs modify installed state. uv resolves declared groups together;
an incompatible unselected group can still prevent locking. Optional dependencies
also participate in the shared resolution, with explicit conflict declarations
available for intentionally incompatible selections. Do not diagnose a lock failure
as “the installer ignored my group flag” without separating resolution from sync.
([uv dependency groups, defaults, extras, and conflicts](https://docs.astral.sh/uv/concepts/projects/dependencies/),
mutable documentation recorded on 2026-11-04.)

An upstream release does not by itself make an existing uv lock stale. Existing
locked versions remain preferred while they satisfy constraints. Upgrade intent is
explicit, for example:

```sh
uv lock --upgrade-package urllib3
```

This requests a resolution/lock update for the named package, not an installation or
a guarantee that no transitive version changes. `uv lock --upgrade` requests a broad
upgrade. Review the resulting graph separately from syncing/testing the selected
environment; do not use `--frozen` as an upgrade or freshness check.

## Separate Resolution From Artifact Installation

A resolver finding compatible version metadata is not a successful target install.
The selected interpreter/OS/architecture still needs a compatible wheel or a source
build with its required toolchain and system libraries. A universal lock can contain
marker-dependent alternatives without proving that each artifact builds or executes
on every supported target. When resolution succeeds but installation fails, inspect
the selected artifact, wheel tags, source-build requirements, and target interpreter
before changing version constraints. ([uv resolution and required environments](https://docs.astral.sh/uv/concepts/resolution/).)

For a new or unconfigured project that permits a manager choice, uv with a committed
`uv.lock` and an uncommitted project `.venv` is one coherent proposed starting point.
The evidence does not show uv is superior to Poetry, pip-tools, Conda, or another
working manager. Preserve the existing manager, lock format, sync behavior, and
interpreter selection in a brownfield project unless the requested outcome requires a
scoped migration.

## Evaluate A Named Dependency Without A Score

Start with the capability and constraints. Check whether the standard library or an
existing dependency already meets the need; then examine the actual candidate's
identity/source, compatibility, maintenance and release evidence, vulnerability
reporting, license clarity, installation behavior, and transitive graph. OpenSSF's
guide provides diligence questions, not a universal cutoff or numeric package-health
score. Popularity and badges are leads, not proof. An outcome may be no-add, add,
replace, or defer, but this reference has not evaluated a candidate. ([OpenSSF
Concise Guide](https://best.openssf.org/Concise-Guide-for-Evaluating-Open-Source-Software.html).)

### Follow The Graph Beyond The Top-Level Package

Evaluation evidence needs a scope. The runtime set for one selected extra/group can
differ from the complete lock, and both can omit build-system dependencies resolved
in an isolated build. Identify the candidate's authentic distribution/source and
resolved direct/transitive versions; distinguish packages executed during builds
from those shipped to consumers. Otherwise “no issue found” may mean only that a
smaller graph was visible.

GitHub's [dependency graph documentation](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-graph-data)
explains that static manifest analysis can miss build-time resolution; supported
dependency-submission paths can supplement it. Lockfiles improve version visibility
but do not make every build input visible to every scanner. Its [dependency review](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-review)
surfaces license/vulnerability data for changes it can observe, not an audit of
all package code, build hooks, or platform variants. These are that platform's
documented visibility limits, not a universal graph-completeness guarantee.

License review likewise follows the graph and intended use, not just the direct
package's badge. Inspect declared SPDX expressions, shipped license files, transitive
components, and bundled material. PyPA specifies that `License-Expression` applies to
the distribution archive carrying it, not automatically every upstream artifact or
the whole project. Missing metadata remains a gap; a scanner's license match does
not decide compatibility or obligations for a particular product/jurisdiction.
([PyPA license expressions](https://packaging.python.org/en/latest/specifications/license-expression/)
and [Core Metadata licensing fields](https://packaging.python.org/en/latest/specifications/core-metadata/#license-expression).)

Maintenance and security signals need the same restraint. Recent releases,
maintainer communication, supported Python/platform versions, vulnerability response,
and tests are evidence dimensions, not interchangeable pass/fail badges. OpenSSF
Scorecard explicitly describes heuristics, false positives/negatives, and aggregate
scores that hide individual checks. Investigate the relevant findings rather than
treating a score or absence of known advisories as proof of suitability. ([OpenSSF
Scorecard limits](https://github.com/ossf/scorecard/blob/main/README.md).)

## Brownfield And Version Limits

Keep the manager's declaration, lock, dependency categories, interpreter request,
groups/extras, and CI resolution behavior intact unless a specific authorized outcome
changes them. A lock or successful sync does not establish runtime behavior for every
declared Python/platform target.

The lock-freshness example is backed by uv 0.13.5 documentation. Additional sync,
selection, upgrade, and resolution explanations preserve mutable uv documentation
recorded on 2026-11-04; those pages were not release-pinned by that research. PyPA,
GitHub, and OpenSSF links also preserve recorded guidance rather than fresh validation.
Check the actual manager version and configuration before using the illustrative
commands; do not translate one manager's group syntax or lock guarantees into another
manager's workflow. PEP 735 is a historical design record; the maintained PyPA groups
specification linked above supplies the publication boundary.

## Related Domains

- Declared versus tested runtime support belongs to [Project Context and Layout](project-context-and-layout.md).
- Metadata and artifacts belong to [Distribution Artifacts](distribution-artifacts.md).
- Checker import environments belong to [Static Quality](static-quality.md).
