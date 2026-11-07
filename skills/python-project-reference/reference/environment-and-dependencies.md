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
dev = ["pytest", "ruff"]
```

Here `urllib3` is a runtime requirement, `postgres` is a published optional feature,
and `dev` is for development/task tools. PyPA specifies that dependency groups are not
emitted as package metadata; group-install commands are manager-specific. Names and
dependencies are illustrative and claim no compatibility result. (Dossier C02, C14,
C26; [PyPA metadata specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/) and [dependency groups specification](https://packaging.python.org/en/latest/specifications/dependency-groups/).)

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
the whole runtime image. (C13; [uv 0.13.5 locking and syncing](https://github.com/astral-sh/uv/blob/0.13.5/docs/concepts/projects/sync.md).)

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
replace, or defer, but this reference has not evaluated a candidate. (C26; [OpenSSF
Concise Guide](https://best.openssf.org/Concise-Guide-for-Evaluating-Open-Source-Software.html).)

## Brownfield And Version Limits

Keep the manager's declaration, lock, dependency categories, interpreter request,
groups/extras, and CI resolution behavior intact unless a specific authorized outcome
changes them. A lock or successful sync does not establish runtime behavior for every
declared Python/platform target.

The lock/sync example is specific to uv 0.13.5. The PyPA dependency-groups page is a
mutable `/en/latest/` specification snapshot. Check the actual manager version and
project configuration before relying on behavior; do not translate one manager's group
syntax or lock guarantees into another manager's workflow.

## Related Domains

- Declared versus tested runtime support belongs to [Project Context and Layout](project-context-and-layout.md).
- Metadata and artifacts belong to [Distribution Artifacts](distribution-artifacts.md).
- Checker import environments belong to [Static Quality](static-quality.md).
