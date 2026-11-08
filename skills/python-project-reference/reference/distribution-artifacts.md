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
full set of targets a project tested. ([PyPA `pyproject.toml`](https://packaging.python.org/en/latest/specifications/pyproject-toml/), [wheel format](https://packaging.python.org/en/latest/specifications/binary-distribution-format/), [sdist format](https://packaging.python.org/en/latest/specifications/source-distribution-format/), and [PEP 517](https://peps.python.org/pep-0517/).)

## Work A Missing-Resource Failure Back To The Artifact

Assume a package reads `templates/report.html`. It works from the checkout but raises
a missing-resource error after a regular install. The source tree is not the consumer
artifact: inspect the built wheel and sdist for the package and resource, then inspect
the selected backend's package-discovery and package-data rules. The standard sdist
format does not guarantee that this project-specific template is included.

The build declaration connects the frontend to the selected backend and its build-time
requirements:

```toml
[build-system]
requires = ["setuptools>=84.2.1"]
build-backend = "setuptools.build_meta"
```

Here `build` is the frontend invoked by `python -m build`; setuptools is the backend
named by `build-backend`; and `requires` supplies backend requirements to the frontend.
With `build` 1.6.1's default isolated build, those requirements are installed in a
temporary build environment. That environment is for building, not the package's
consumer/runtime dependencies or the project's locked development environment. A
successful isolated build therefore does not prove runtime dependencies are available
to an installed application. Frontend/backend responsibilities and defaults are
version-specific; the selected backend, frontend, and versions must match the actual
project. ([PyPA `pyproject.toml` specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/#declaring-the-build-backend), [PEP 517](https://peps.python.org/pep-0517/), [build 1.6.1 build isolation](https://build.pypa.io/en/latest/explanation/how-it-works.html#build-isolation-explained).)

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
package metadata ([PyPA dependency groups specification](https://packaging.python.org/en/latest/specifications/dependency-groups/)).

This setuptools excerpt illustrates an explicit `src/` package and resource pattern:

```toml
[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
acme_catalog = ["templates/*.html", "py.typed", "*.pyi"]
```

Assumption: the selected backend is setuptools and the resource is under the
`acme_catalog` package. Setuptools v84.2.1 documents `package_data` patterns and
discovery behavior; actual contents depend on the project's files and effective
configuration. This is not a tested artifact or a universal backend recommendation.
([setuptools v84.2.1 package data](https://github.com/pypa/setuptools/blob/v84.2.1/docs/userguide/datafiles.rst) and [package discovery](https://github.com/pypa/setuptools/blob/v84.2.1/docs/userguide/package_discovery.rst).)

Discovery and data inclusion are separate checks: for this example, `where = ["src"]`
locates packages beneath `src/`, while the package-data pattern selects the template.
Setuptools automatic package discovery applies only when `packages` and `py_modules`
are not explicitly set; explicit package selection changes that path. If the
distribution promises inline typing, verify that `py.typed` is included in the
installed package (and that any promised `.pyi` stubs are included too). The typing
specification defines the marker as the signal that a package supports typing; it
does not guarantee that a backend will package it. Include it through the backend's
package-data rules and inspect the artifact rather than assuming source-tree presence
is sufficient. ([setuptools v84.2.1 discovery](https://github.com/pypa/setuptools/blob/v84.2.1/docs/userguide/package_discovery.rst), [package data](https://github.com/pypa/setuptools/blob/v84.2.1/docs/userguide/datafiles.rst), [typing `py.typed` guidance](https://typing.python.org/en/latest/spec/distributing.html#packaging-type-information).)

The `build` frontend 1.6.1 documents `python -m build` as building an sdist, extracting
it, then building a wheel from that archive by default. That path can expose source
files missing from the sdist, unlike building a wheel only from the checkout. A regular
local install is closer to consumer installation than an editable install, but the
retrieved pip page identified itself as mutable v27.0.dev0 documentation; do not treat
it as a stable target contract. These are failure-diagnosis examples, not commands run
here. ([build 1.6.1 README](https://github.com/pypa/build/blob/1.6.1/README.md) and [pip local project installs](https://pip.pypa.io/en/latest/topics/local-project-installs/).)

For a consumer-like check after reviewing the target's backend/installer versions, build
both artifacts, create a clean environment, install the wheel regularly, and verify the
installed import and resource from outside the checkout. Then separately test building
and installing from the sdist when that path is promised:

```sh
python -m build
python -m venv /tmp/acme-consumer
/tmp/acme-consumer/bin/python -m pip install dist/acme_catalog-1.0.0-py3-none-any.whl
cd /tmp
/tmp/acme-consumer/bin/python -c 'from importlib.resources import files; import acme_catalog; print(acme_catalog.__file__); assert files("acme_catalog").joinpath("templates/report.html").is_file(); assert files("acme_catalog").joinpath("py.typed").is_file()'
python -m venv /tmp/acme-sdist-consumer
/tmp/acme-sdist-consumer/bin/python -m pip install /path/to/project/dist/acme_catalog-1.0.0.tar.gz
/tmp/acme-sdist-consumer/bin/python -c 'from importlib.resources import files; import acme_catalog; print(acme_catalog.__file__); assert files("acme_catalog").joinpath("templates/report.html").is_file(); assert files("acme_catalog").joinpath("py.typed").is_file()'
```

The wheel name/interpreter command above are illustrative, assume a pure-Python
wheel, a promised `py.typed` marker, and POSIX shell; omit the marker assertion when
the distribution does not promise typing, and substitute actual artifact/resource
names and supported platform. For promised stubs, additionally assert the exact
installed `.pyi` paths or inspect their presence in both artifacts. Test the
sdist path in another clean environment, since installing the sdist directly exercises
the consumer build path. Assert that the import resolves to the
environment's installed package and that the resource check is true; printing a path
alone is diagnostic, not a test assertion. A regular install avoids the editable
checkout path that can conceal omissions. These commands are guidance, not executed
here. The pip documentation consulted was mutable v27.0.dev0, so verify actual
installer behavior before relying on its details.

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
