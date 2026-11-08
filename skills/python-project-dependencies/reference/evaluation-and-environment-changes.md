# Evaluation And Environment Changes

## Decide Whether A Dependency Is Needed Before Changing State

A dependency decision starts with a capability and constraints, not a package's
popularity. Check the standard library, existing project code, and already approved
dependencies before adding another component. Each new direct requirement can bring
transitive code, installation requirements, and support obligations; the relevant
question is whether that cost buys a needed capability
([OpenSSF evaluation guide](https://best.openssf.org/Concise-Guide-for-Evaluating-Open-Source-Software.html)).

Keep evaluation read-only unless specific additional effects are authorized. Reading
metadata or a lock is not permission to resolve, install, update that lock, or sync an
environment. A recommendation to add or replace a package also does not itself grant
permission to implement the recommendation.

Use one explicit decision:

- **No-add:** the requirement is absent or existing capabilities adequately meet it.
- **Add:** a concrete unmet need and proportionate evidence support the candidate under
  the project's constraints and approval requirements.
- **Replace:** an existing component has a concrete problem and the migration's
  compatibility/cost is understood; actual removal still needs authorization.
- **Defer:** material evidence or an owner's decision is missing; identify what would
  resolve the gap rather than assigning a low confidence score and proceeding anyway.

## Worked Decision Record: An Unnecessary Second HTTP Client

Assume a hypothetical service already declares urllib3 and has a tested project-owned
`fetch_json` wrapper. The request is to consider adding httpx for a single synchronous
HTTPS JSON lookup. Inspection of that project's wrapper and tests establishes that
the existing path already supplies the needed request, failure reporting, and explicit
timeouts. Native async operation, a new protocol, and a new public API are not required.

A useful record would say:

- **Need:** one synchronous lookup through the existing outbound-request boundary.
- **Targets:** preserve the project's declared Python/platform range; do not expand it
  merely because the evaluator has a newer local interpreter.
- **Existing alternative:** the declared client and project wrapper already meet this
  task's behavior. Cite the actual wrapper and tests in a real record.
- **Candidate:** httpx, raised by the request; no release was selected or installed.
- **Decision:** no-add. A second client adds another maintenance/configuration path
  without satisfying an unmet requirement in this scenario.
- **Evidence limit:** this is a project-fit decision, not a security, license, or
  comparative performance verdict about httpx. No candidate release or transitive graph
  was audited for the illustrative record.
- **Reopen when:** an actual interface/workload need cannot be met by the current
  boundary; then evaluate a named release and target graph rather than reusing this decision.
- **Effects:** none; declarations, lock, interpreter selection, and environment stay unchanged.

The package names do not make the conclusion universal. If existing support is
unverified, inspect it or defer; do not fabricate a favorable capability comparison.
The record exposes why no candidate audit is needed for this bounded no-add decision,
while an add/replace decision would require more evidence.

## Inspect Evidence That Can Change The Decision

For a material candidate/version change, examine these concerns independently:

- **Fit and compatibility:** required API behavior, API stability, supported Python and
  platforms, artifacts available for those targets, and expected installation/build
  prerequisites. A successful resolve on the evaluator's machine is not target validation.
- **Maintenance and support:** releases, maintainer communication, supported versions,
  issue/security response, tests, and continuity. One maintainer is not automatic failure;
  a recent release or popular badge is not proof of safe or suitable code.
- **Identity and security:** authentic package/source, direct and transitive components,
  known vulnerabilities relevant to the version/use, response practices, and blind spots
  in the available tooling. A clean known-issue check cannot exclude unknown problems.
- **License evidence:** declared expression, shipped license files, relevant transitive
  components, and intended use. Escalate legal/policy interpretation rather than treating
  a scanner match as approval.

OpenSSF provides investigation dimensions, not universal release-age cutoffs or a
scoring formula. Scorecard explicitly describes heuristics, false positives/negatives,
and aggregate-score limitations
([evaluation guidance](https://best.openssf.org/Concise-Guide-for-Evaluating-Open-Source-Software.html),
[Scorecard limitations](https://github.com/ossf/scorecard/blob/main/README.md)).

GitHub dependency review/graph data is bounded by supported ecosystems and available
manifest, lock, or submitted data. Static detection can miss build-resolved or
unsubmitted components, so an apparently complete dashboard is not a complete graph
audit ([dependency review](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-review),
[graph detection](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-graph-data)).
PyPA's license expression applies to the archive carrying the metadata, not
automatically every upstream artifact or dependency
([license expressions](https://packaging.python.org/en/latest/specifications/license-expression/),
[Core Metadata](https://packaging.python.org/en/latest/specifications/core-metadata/)).

## Separate Declarations, Interpreter, Resolution, And Installation

These project facts answer different questions:

- `requires-python` expresses declared compatibility intent.
- `.python-version` is uv's default interpreter request, not the full support range.
- `pyproject.toml` declares metadata and dependency requirements.
- `uv.lock` records a universal resolution with exact versions and markers across
  Python/platform variation; it is not the same thing as packages currently installed.
- `.venv` is the installed project environment. uv creates it and the lock lazily when
  needed and recommends leaving the environment out of version control.

These are uv project conventions, not a required migration for Poetry, pip-tools,
Conda, or another working manager
([uv project workflow](https://docs.astral.sh/uv/guides/projects/),
[structure and files](https://docs.astral.sh/uv/concepts/projects/layout/)). A venv
isolates installed packages but shares the base standard library; neither it nor a
package lock recreates the OS, compiler, system libraries, interpreter binary, or
byte-identical build results
([PyPA virtual environments](https://packaging.python.org/en/latest/specifications/virtual-environments/)).

Universal resolution considers markers and the supported Python range, but required
environments and available wheels still constrain actual installations. Keep declared
support, selected interpreter, tested matrix, and artifact availability distinct
([uv resolution](https://docs.astral.sh/uv/concepts/resolution/),
[Python selection](https://docs.astral.sh/uv/concepts/python-versions/)).

## Put Requirements In The Right Category

For a hypothetical package, these declarations have different consumers:

```toml
[project]
dependencies = ["httpx"]

[project.optional-dependencies]
postgres = ["psycopg"]

[dependency-groups]
lint = ["ruff"]
```

Here the HTTP client is a runtime requirement, `postgres` is a published optional
feature, and `lint` is internal development tooling. This fragment illustrates roles;
it does not recommend those dependencies or establish compatible versions. Groups are
not emitted as distribution metadata, and the standard does not define one installer
interface ([PyPA Dependency Groups](https://packaging.python.org/en/latest/specifications/dependency-groups/)).

uv resolves declared groups together and selects `dev` by default; incompatible
groups may need explicit conflict handling or a different project arrangement.
uv-specific source overrides do not become portable metadata for another tool
([uv 0.13.5 dependency management](https://github.com/astral-sh/uv/blob/0.13.5/docs/concepts/projects/dependencies.md)).
Do not install every group/extra merely because it appears in the declaration.

## Analyze Command Effects Before Execution

For a project actually using uv **0.13.5**, the documented examples
`uv add httpx` and `uv add --group lint ruff` update the corresponding declaration,
lock, and project environment. They are not read-only ways to investigate a candidate
([uv 0.13.5 dependencies](https://github.com/astral-sh/uv/blob/0.13.5/docs/concepts/projects/dependencies.md)).

Locking resolves requirements; syncing installs the selected subset of that resolution.
uv's normal project invocations can lock and sync automatically. Consequently, even
running a project command can change state unless the selected options/configuration
bound those effects. Inspect the actual invocation rather than equating “run tests”
with “no environment changes.”

For uv 0.13.5:

- `uv sync --locked` refuses a missing/stale lock instead of rewriting it, but still
  synchronizes the environment. It can install packages and remove extraneous ones.
- `--frozen` consumes the existing lock without checking it against metadata. Successful
  frozen execution therefore does not establish currentness.
- `uv sync` is exact by default, while `uv run` uses inexact synchronization by default.
  These can differ in whether extraneous installed packages remain.
- New upstream releases alone do not make the lock stale; upgrades are explicit.

These mechanics come from [uv 0.13.5 locking and syncing](https://github.com/astral-sh/uv/blob/0.13.5/docs/concepts/projects/sync.md).
They distinguish lock protection from environment protection: do not choose a sync
command for an evaluation-only request merely because it cannot rewrite the lock.
Select the actual manager's documented non-rewriting lock-currentness check when that
check is requested; sync only when the target environment effect is also authorized.

## Worked Diagnosis: Frozen Passes But Locked Fails

Assume a declaration changed while `uv.lock` did not. A frozen invocation can run with
the old graph; a locked invocation rejects the mismatch. This is expected evidence
of different checks, not a reason to weaken CI to frozen mode. Inspect the metadata/lock
diff, identify whether resolution is authorized, and report a stale lock until the
authorized manager workflow updates it. Do not hand-edit the resolution or broaden
constraints merely to silence the check.

After an authorized change, review declaration and lock diffs together. For an authorized
sync, record interpreter/platform, manager version, groups/extras, sources, and installed/
removed effects. Run only the requested project checks on stated targets. A clean lock
check or successful sync is not application correctness, all-platform compatibility,
security assurance, or a legal conclusion.

## Preserve Project Choices And Version Scope

Keep the existing manager, interpreter selection, source/index settings, dependency
categories, and CI workflow unless changing them is the requested outcome. uv's GitHub
Actions example illustrates pinned tooling, explicit Python selection, locked sync,
and intended groups/extras; it is not a mandatory CI policy
([uv CI guidance](https://docs.astral.sh/uv/guides/integration/github/)). Standardized
`pylock.toml` and uv's project-specific `uv.lock` are distinct; publishing a standard
does not prove full cross-tool interoperability
([PyPA pylock](https://packaging.python.org/en/latest/specifications/pylock-toml/),
[uv format relationship](https://docs.astral.sh/uv/concepts/projects/layout/)).

The live uv/OpenSSF/PyPA/GitHub sources reflect the historical 2026-11-04 inspection;
the concrete commands above are scoped to uv 0.13.5, separately checked in the supplied
records on 2026-11-06. Preview pylock/audit/malware status was time-sensitive, not a
stable security guarantee ([uv preview](https://docs.astral.sh/uv/concepts/preview/)).
These are not fresh fetches or target installation evidence. Verify actual versions
and effective settings before executable use.

For deeper shared mechanics, explicitly load `python-project-reference` before reading
`python-project-reference -> reference/environment-and-dependencies.md`; use
`python-project-reference -> reference/distribution-artifacts.md` only for the boundary
between dependency state and build artifacts. Artifact production, source behavior,
test edits, and standalone quality outcomes remain separate work.
