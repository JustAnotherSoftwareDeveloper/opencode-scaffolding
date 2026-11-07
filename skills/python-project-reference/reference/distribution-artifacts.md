# Distribution Artifacts

## Confirm The Consumer Install Boundary

Build Python distribution artifacts when the delivery promise is an installable
library, CLI, internal package, or other Python distribution. A service or application
does not need a wheel or sdist just because it contains Python code or a
`pyproject.toml`. Keep source/configuration, artifact production, optional publication,
and consumer installation distinct; this module covers metadata, artifacts, and
installability concepts, not upload or deployment authority.

PyPA separates `[build-system]` (backend and build requirements), `[project]`
(standardized project metadata), and `[tool]` (tool-specific configuration). PEP 517
defines the frontend/backend interface but chooses neither. A wheel is a tagged built
archive; an sdist is a source archive whose standard format does not specify every
project-specific input. A wheel tag states the artifact's compatibility claim, not the
full set of targets a project tested. (Dossier C15; [PyPA `pyproject.toml`](https://packaging.python.org/en/latest/specifications/pyproject-toml/), [wheel format](https://packaging.python.org/en/latest/specifications/binary-distribution-format/), [sdist format](https://packaging.python.org/en/latest/specifications/source-distribution-format/), and [PEP 517](https://peps.python.org/pep-0517/).)

## Work A Missing-Resource Failure Back To The Artifact

Assume a package reads `templates/report.html`. It works from the checkout but raises
a missing-resource error after a regular install. The source tree is not the consumer
artifact: inspect the built wheel and sdist for the package and resource, then inspect
the selected backend's package-discovery and package-data rules. The standard sdist
format does not guarantee that this project-specific template is included.

This metadata fragment describes a hypothetical pure-Python CLI distribution:

```toml
[project]
name = "acme-catalog"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = ["urllib3"]

[project.optional-dependencies]
postgres = ["psycopg"]

[project.scripts]
acme-catalog = "acme_catalog.cli:main"
```

The version, requirement, dependencies, and entry point are illustrative metadata,
not claims that a particular Python target was tested or that these names resolve in a
real package. Runtime requirements and published extras are consumer metadata; test
and lint groups belong to the environment/dependency model and are not emitted as
package metadata (C14; [PyPA dependency groups specification](https://packaging.python.org/en/latest/specifications/dependency-groups/)).

This setuptools excerpt illustrates an explicit `src/` package and resource pattern:

```toml
[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
acme_catalog = ["templates/*.html"]
```

Assumption: the selected backend is setuptools and the resource is under the
`acme_catalog` package. Setuptools v84.2.1 documents `package_data` patterns and
discovery behavior; actual contents depend on the project's files and effective
configuration. This is not a tested artifact or a universal backend recommendation.
(C27, C32; [setuptools v84.2.1 package data](https://github.com/pypa/setuptools/blob/v84.2.1/docs/userguide/datafiles.rst) and [package discovery](https://github.com/pypa/setuptools/blob/v84.2.1/docs/userguide/package_discovery.rst).)

The `build` frontend 1.6.1 documents `python -m build` as building an sdist, extracting
it, then building a wheel from that archive by default. That path can expose source
files missing from the sdist, unlike building a wheel only from the checkout. A regular
local install is closer to consumer installation than an editable install, but the
retrieved pip page identified itself as mutable v27.0.dev0 documentation; do not treat
it as a stable target contract. These are failure-diagnosis examples, not commands run
here. (C27; [build 1.6.1 README](https://github.com/pypa/build/blob/1.6.1/README.md) and [pip local project installs](https://pip.pypa.io/en/latest/topics/local-project-installs/).)

## Match Artifacts To The Promise

For a new library promising both a ready-to-install binary distribution and source
build path, a wheel plus sdist is a reasonable starting artifact set. It is not a
universal artifact-count rule. The intended file inventory, runtime requirements,
extras, entry points, Python requirement, and tested targets should match the consumer
promise. Development dependency groups are not emitted as package metadata.

For a brownfield package, retain the existing backend/frontend, metadata source,
versioning model, file-selection rules, artifact set, import paths, and compatibility
promises. A missing file, wrong wheel tag, or support-metadata mismatch may justify a
requested bounded change; the format specification alone does not choose the fix.
Separate one local build/install result from a claim about all supported targets.

## Evidence Limits

PyPA `/en/latest/` pages are mutable snapshots. Build details above are pinned to build
1.6.1 and setuptools v84.2.1; the pip local-install page is marked v27.0.dev0 and could
not be fetched by an exact version-addressed route. Verify the target's installed
frontend, backend, and installer before relying on those examples. No artifact was
built or inspected here, and no target package's contents are known.

## Related Domains

- Project kind, runtime support, and source layout belong to [Project Context and Layout](project-context-and-layout.md).
- Dependency roles, locks, and resolution belong to [Environment and Dependencies](environment-and-dependencies.md).
- Sensitive values in shipped files belong to [Secure Configuration and Data Handling](secure-configuration-and-data-handling.md).
