# Metadata, Build, And Installation

## Start With The Consumer Delivery Promise

Use Python distribution work for an actual installable library, internal package,
CLI, or other promised distribution. Python source or a `pyproject.toml` does not
alone establish that a service needs a wheel. Building, publishing to an index,
installing, and deploying an application are distinct stages
([PyPA Packaging Flow](https://packaging.python.org/en/latest/flow/),
[packaging overview](https://packaging.python.org/en/latest/overview/)).

Record the requested artifact types, expected imports/resources/entry points, supported
Python/platform targets, and output location. Preserve the existing backend, frontend,
version source, file-selection rules, and release promises. Do not add an sdist, a
platform wheel, a new backend, or a publishing step merely because it is common.

## Distinguish Metadata And Tool Responsibilities

`pyproject.toml` separates three concerns:

- `[build-system]` declares build requirements and the backend interface.
- `[project]` carries standardized distribution metadata such as identity, version,
  supported Python, runtime requirements, optional features, and entry points.
- `[tool]` contains tool-specific configuration; package discovery and resource inclusion
  still depend on the selected backend.

The current PyPA specification requires static `name` when using `[project]`; version
is either static or explicitly dynamic for the backend to supply. Do not define it
both ways. A user guide's normal recommendation to include `[build-system]` differs
from the formal specification's omission/default semantics; use the formal specification
for edge cases instead of forcing every established project into a new metadata model
([pyproject specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/),
[writing pyproject](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)).

A build frontend prepares the build context and invokes hooks; the backend discovers
project files, produces metadata, and creates artifacts. An installer selects and
installs compatible artifacts, potentially invoking a source build when needed. These
roles can overlap in a tool but are not interchangeable responsibilities
([PEP 517](https://peps.python.org/pep-0517/),
[PEP 518](https://peps.python.org/pep-0518/),
[build backend explanation](https://build.pypa.io/en/latest/explanation/build-backends.html)).
Build isolation installs backend requirements in a separate build environment; it
does not lock the full application runtime or prove reproducible output.

## Worked Metadata: A Small Installable CLI

Assume an existing backend already packages `src/report_convert`, and the requested
delivery is a pure-Python CLI with no third-party runtime requirements:

```toml
[project]
name = "report-convert"
version = "1.0.0"
requires-python = ">=3.11"
description = "Convert local reports into a text summary"
readme = "README.md"

[project.scripts]
report-convert = "report_convert.cli:main"
```

This is a standardized project-metadata fragment, not a complete backend configuration.
The name/version and supported range are hypothetical contract choices, not tested
results. The existing `[build-system]` remains unchanged. Check that the readme exists,
the backend includes the intended package, and the installed command resolves to the
promised callable ([entry-points specification](https://packaging.python.org/en/latest/specifications/entry-points/)).

If the project already derives its version through the backend, a static `version`
would be the wrong change. Its metadata might instead contain:

```toml
[project]
name = "report-convert"
dynamic = ["version"]
```

The backend-specific source needed to compute that version must still be available
when building from the sdist. Declaring dynamic metadata does not create its value or
guarantee the needed source file was included.

Runtime requirements and published extras are installer-facing metadata; internal
lint/test groups are not. Do not fix an installation failure by moving all development
tools into runtime dependencies
([Dependency Groups](https://packaging.python.org/en/latest/specifications/dependency-groups/)).
Version identifiers and comparison rules also do not decide SemVer, deprecation policy,
or release cadence ([Version Specifiers](https://packaging.python.org/en/latest/specifications/version-specifiers/)).

## Build The Promised Artifacts Through The Existing Frontend

For a project actually using PyPA **build 1.6.1**, the documented default is:

```sh
python -m build
```

It builds an sdist, extracts it, and then builds a wheel from that source archive.
This can expose a file missing from the sdist that a checkout-only wheel build would
still find. `python -m build --sdist` and `python -m build --wheel` request a single
format; the documentation also accepts an sdist archive as input for a wheel build
([build 1.6.1 README](https://github.com/pypa/build/blob/1.6.1/README.md),
[Basic Usage](https://build.pypa.io/en/latest/how-to/basic-usage.html)).

Do not substitute that default for a request promising only one format, or assume
every frontend uses the same strategy. Build isolation can download/install build
requirements and execute backend code; disabling it transfers preparation responsibility
to the caller, not a guarantee of safer or more reproducible output
([How It Works](https://build.pypa.io/en/latest/explanation/how-it-works.html)).
Authorize the exact build, output paths, dependency/network effects, and any overwrite
before execution. An unavailable frontend does not authorize installing/upgrading it.

## Inspect Contents Before Trusting The Filename

A wheel is a ZIP-format built distribution with install-layout files and metadata;
its filename encodes Python, ABI, and platform compatibility tags. Those tags state a
compatibility claim, not a matrix already exercised by tests
([wheel specification](https://packaging.python.org/en/latest/specifications/binary-distribution-format/)).

Inspect the actual artifact for the expected import package, resources, metadata,
entry-point declarations, and any promised type information. Check identity/version,
Python requirement, requirements/extras, and license files against the project contract.
Also inspect for unintended configuration, credentials, local data, or build detritus.
A successful build or archive listing alone does not establish installability.

The standardized sdist is a gzip tar archive with a name/version root, `pyproject.toml`,
and PKG-INFO; the format does not prescribe every additional project file. Compare it
with the actual sources and backend inputs required to build the wheel. Use safe
archive inspection/extraction: the current specification requires `tarfile.data_filter()`
or its specified equivalent safeguards for consumers
([sdist specification](https://packaging.python.org/en/latest/specifications/source-distribution-format/)).

Core Metadata was observed as **2.6**, approved May 2026. Metadata consumers can lag
the specification, so distinguish emitted metadata version from acceptance by the
actual target installer. License-expression metadata describes the archive carrying
it, not a legal audit of every upstream component
([Core Metadata](https://packaging.python.org/en/latest/specifications/core-metadata/)).

## Worked Diagnosis: Checkout Works, Installed CLI Fails

Suppose `report_convert` reads a packaged `templates/summary.txt`. The checkout command
works, but the installed command raises a missing-resource error. Inspect both wheel
and sdist before changing production code:

- **Absent from both:** investigate the backend's discovery/resource-inclusion rules.
- **Present in checkout-built wheel but absent from sdist:** the source archive may
  omit an input; a wheel built from the sdist can reproduce the consumer build failure.
- **Present in the artifact but runtime lookup fails:** record an installed-resource
  lookup defect for the production owner rather than silently editing runtime behavior.
- **Unexpected import location:** determine whether checkout/PYTHONPATH/editable state
  masked the package actually installed in the test environment.

The formats do not choose a backend-specific resource rule. Explicitly load
`python-project-reference` and read
`python-project-reference -> reference/distribution-artifacts.md` for its qualified
resource-inclusion example; use the actual backend/version documentation for a fix.
Keep distribution-configuration changes separate from production lookup changes.

## Test The Artifact, Not Just The Checkout

A clean target-appropriate install tests a different promise from a developer or
editable environment. Pip normally prefers compatible wheels and can build/cache a
wheel from an sdist, but artifact availability, build prerequisites, dependencies,
and index constraints still determine success
([Installing Packages](https://packaging.python.org/en/latest/tutorials/installing-packages/)).

For a worked example, assume the project root is `/work/report-convert`, the requested
target is Python 3.11, the approved installer is pip, and the build actually produced
the exact wheel named below. The temporary path must be unused and separately
authorized; the example is not an instruction to overwrite an existing environment:

```sh
python3.11 -m venv /tmp/opencode/report-convert-install
/tmp/opencode/report-convert-install/bin/python -m pip install /work/report-convert/dist/report_convert-1.0.0-py3-none-any.whl
/tmp/opencode/report-convert-install/bin/python -I -c "import report_convert; print(report_convert.__file__)"
/tmp/opencode/report-convert-install/bin/report-convert --help
```

These are explanatory commands, not executed results or an inferred wheel name.
Select the actual target interpreter and approved installer version first. Run the
installed command outside the checkout; isolated import mode helps expose accidental
dependence on checkout/PYTHONPATH state. For this hypothetical CLI, `--help` is a
promised interface: also exercise the specific conversion/resource path that previously
failed, since help alone may never load the missing template.

Installation can contact configured indexes and install dependencies; record and
authorize those effects even when the direct input is a local archive. Do not upgrade
pip as an incidental preparation step. A request promising an sdist also needs a
separate source-archive build/install check where applicable; use a fresh environment
for each artifact so an already installed wheel cannot mask a broken source path.

Report exact filenames/tags, tools/versions, interpreter/platform, dependency/index
constraints, commands, inspected contents, installed imports/entry points, and results.
One pure-Python wheel installed on one interpreter does not validate every declared
target, and native-code wheels may need additional ABI/platform combinations.

## Keep Publication And Other Outcomes Separate

A private index is distribution infrastructure, not a build backend or an environment
sync mechanism. Its HTTPS/client-configuration guidance is not a complete security
model ([simple repository hosting](https://packaging.python.org/en/latest/guides/hosting-your-own-index/),
[Simple Repository API](https://packaging.python.org/en/latest/specifications/simple-repository-api/)).
Do not upload artifacts, configure registry authentication, or deploy the application
as part of a build/install request.

Likewise, provenance is not artifact correctness: PyPI attestations can bind file digests
to identity/provenance claims without proving safe source or build environments
([PyPI attestation security model](https://docs.pypi.org/attestations/security-model/)).
A successful local build/install establishes neither publication nor such verification.

## Version Scope And Further Context

The build command behavior is scoped to **1.6.1**. PyPA/PEP/PyPI and build `/en/latest/`
pages were historically inspected in November 2026 and are mutable, not freshly fetched
here. Earlier records associate an installation lookup with pip 27.0; the shared
reference more specifically identifies its mutable local-install page as **27.0.dev0**.
Neither is an assumption about an installed pip release. Verify the selected
frontend/backend/installer and use its documented workflow before executing examples.
PyPA's tool guidance explicitly avoids a blanket backend recommendation
([tool recommendations](https://packaging.python.org/en/latest/guides/tool-recommendations/)).

For support/import context, explicitly load `python-project-reference` and read
`python-project-reference -> reference/project-context-and-layout.md`; for dependency
versus artifact state, use
`python-project-reference -> reference/environment-and-dependencies.md`. For sensitive
artifact contents, use
`python-project-reference -> reference/secure-configuration-and-data-handling.md`.
Keep shared precedence/adoption choices in
`python-project-reference -> reference/project-baseline-and-adoption.md` rather than
turning example metadata into mandatory project policy.
