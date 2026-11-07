---
name: python-package-distribution
description: "Use when a Python project needs requested distribution metadata, build configuration, wheel or sdist artifacts, or installability checks."
selection:
  role: owner
  tags:
    actions: [inspect, configure, build, validate]
    inputs: [Python project, distribution request]
    outputs: [Python distribution artifacts and validation evidence]
    topics: [package distribution]
    environments: [Python package, installable CLI]
    constraints: [requested authorized effects only, preserve compatibility promises]
  use_when:
    - a request owns Python distribution metadata or build configuration changes
    - a request asks to build or validate promised wheel or sdist artifacts and installations
  not_for:
    - choosing dependencies, resolving locks, or synchronizing project environments
    - changing Python source or tests, uploading artifacts, administering registries, or deploying applications
class: operation
---

# Distribution Workflow

Own requested Python distribution metadata and build configuration, promised wheel or source-distribution (sdist) artifacts, artifact contents, and relevant install checks. Do not upload, administer a package registry, or deploy an application; publishing and installation are separate lifecycle stages (DP CL-01, CL-11). Build only when the requested delivery is a Python distribution, such as a library, internal package, or installable CLI; Python code or `pyproject.toml` alone does not establish that need (DP CL-09).

## Normalize Input

Normalize the request into one project input: project root and kind; requested metadata/configuration changes; artifact types and output location; documented version source, backend/frontend, and existing commands; supported Python/platform/runtime targets and wheel-tag promises; expected contents and entry points; clean install targets; and the exact authorized build, configuration, and temporary-environment effects.

Block before writes or builds if the project/request or effect authorization is missing. If distribution applicability, artifact promises, or a target needed for a requested check is unclear, ask rather than infer. Mark only the affected check as deferred when a non-blocking target is unspecified; never report it as passed.

Apply precedence: preserve existing project configuration and compatibility/release promises first, applicable approved local policy second, and proposed defaults only for a new or unconfigured project when the request permits a choice. Keep repository-specific `scripts/python/` practices local. Supplied evidence does not establish comparative outcomes, universal thresholds, enterprise policy, or topology effectiveness.

## Procedure

1. **Bound the delivery.** Confirm the requested consumer outcome is a Python distribution. Separate package installation from full application deployment. Record the exact requested artifact set; do not add an sdist, wheel, platform tag, CLI, or metadata field merely because it is common.
2. **Inspect the existing contract.** Read the current packaging configuration and release process. Identify the established frontend/backend, static or generated version source, distribution metadata, file-selection rules, artifact names/tags, supported targets, import paths, and entry points. Preserve these unless the authorized request requires a change; make unresolved compatibility or policy conflicts visible before acting.
3. **Establish applicable evidence.** Selectively load `python-project-reference -> reference/distribution-artifacts.md`; use only the additional exact loads under `Docs` when target support, compatibility promises, dependency boundaries, or artifact sensitivity make them relevant. These references are passive and non-transitive. Verify exact version-sensitive syntax and behavior against the target's documentation/version. Fetch current primary documentation only when a separate authorization permits that specific check. Do not install or upgrade tools without authorization. If a target tool/version or source-access authorization is missing, name the exact unresolved detail and needed source/version, mark that action non-executable, and provide a bounded separately authorized refresh handoff.
4. **Make only authorized metadata/configuration changes.** Preserve the selected backend and frontend. When a standardized `[project]` declaration applies, check fields such as name, static or backend-provided version, `requires-python`, runtime requirements/extras, readme/license metadata, and promised entry points against the current specification and actual project contract (DP CL-02, CL-06–CL-08). Distinguish internal dependency groups from published requirements/extras; do not change dependency/environment state or choose an API/release policy (DP CL-07–CL-08). A new backend or metadata model is a project choice, not a required migration (DP CL-13).
5. **Build the promised artifacts.** Use the existing authorized frontend and output location; avoid overwriting or deleting existing artifacts without permission. For PyPA `build` 1.6.1, the observed default `python -m build` command creates an sdist, extracts it, then builds a wheel from the extracted sdist; `python -m build --sdist` and `python -m build --wheel` select one format. Its documentation also accepts an sdist archive as input and builds a wheel from it (DP CL-03). Use these commands only when the target actually uses that frontend/version and record the exact command; otherwise use the selected frontend's target-version documentation. If the needed tool/version behavior is unknown, defer that action until verified; if the needed tool is unavailable and installing it is not authorized, stop that action and report the blocker.
6. **Inspect artifacts against the promise.** Record each actual filename, type, metadata version where available, and wheel Python/ABI/platform tags. Inspect wheel install-layout files and metadata and the sdist's standardized structure plus project-specific source/build inputs. Compare both with the requested contents, inclusion rules, metadata, and supported targets; check for unintended or sensitive files when relevant. A filename, tag, archive listing, or successful build alone does not prove installability or the full support matrix (DP CL-04–CL-06).
7. **Test clean installations.** For every requested target and promised artifact, install that exact local wheel in a fresh target-appropriate environment using the project's approved installer; test a promised sdist by building/installing from that archive as relevant. Do not reuse the checkout or developer environment as the sole evidence. Where promised, exercise import paths, declared extras, or installed entry points. Record Python/platform, installer and backend/frontend versions, exact commands, dependency/index constraints, and result (DP CL-05–CL-06). Do not change dependency declarations to work around a failed install; report the failure or route a distinct dependency decision separately.
8. **Report the outcome.** Distinguish completed changes, artifact names/tags, content checks, and successful installs from failed, deferred, or untested targets. State actual tool versions and exact commands, the tested subset and remaining support matrix, any blocker/refresh handoff, and all effects. Do not claim reproducibility, universal compatibility, policy approval, upload, or deployment from local build/install evidence (DP CL-03, CL-06, CL-09, CL-13).

## Self-Validation

- Every write and build/install effect is requested, authorized, and confined to the project metadata/configuration, requested artifacts, or approved temporary test environment.
- Existing backend/frontend, version source, artifact promises, tags, compatibility range, and consumer interfaces are preserved unless an authorized change explicitly addresses them.
- Each promised artifact's metadata, filename/tags, contents, build-from-sdist behavior where relevant, and clean target-appropriate installation are checked or explicitly reported as failed/deferred.
- The report identifies exact artifact names, commands, tool versions, target environments, outcomes, and untested scope; no upload, registry, deployment, or unverified support claim is included.
- Every version-sensitive procedure detail has a source, applicable version, access date/context, and limits below, or remains explicitly non-executable with a bounded authorized refresh handoff.
- Filled content uses semantic prose forms and contains no Markdown tables.

## Expected Output

Return the requested metadata/build-configuration changes and promised artifacts only, with an outcome report covering artifact paths/names/tags, inspected contents, metadata, exact tools/versions/commands, clean install evidence by target, failures or deferrals, and untested scope. If a check fails or evidence is deferred, report that status instead of presenting the distribution as validated.

## Version-Sensitive Evidence

Selected primary publisher pages were fetched on **2026-11-06** using `functions.webfetch`; the supervisor confirmed the separate authorization covered these targeted PyPA/PEP checks. The statements below are based on the observed pages and the mapped source/claim records, not on authorization alone. PyPA `/en/latest/` pages are mutable snapshots; their access date is not an immutable revision or a target project's tool version. This evidence supports the version-qualified examples here; it neither assumes a real target's tool versions nor establishes any project's installed versions or compatibility.

- **PyPA `pyproject.toml` specification** ([SRC-02](https://packaging.python.org/en/latest/specifications/pyproject-toml/)): current formal specification snapshot, accessed 2026-11-06; it identifies `[build-system]` and standardized `[project]` metadata, including required static `name` and static-or-dynamic `version`. The page is mutable and does not select a backend or prove a target backend supports every field.
- **PyPA Core Metadata 2.6** ([SRC-03](https://packaging.python.org/en/latest/specifications/core-metadata/)): page states version 2.6, approved May 2026; accessed 2026-11-06. Installer support may lag, and this does not establish target metadata acceptance.
- **PEP 517 and PEP 518** ([SRC-04](https://peps.python.org/pep-0517/), [SRC-05](https://peps.python.org/pep-0518/)): specifications accessed 2026-11-06; define frontend/backend and build-requirement interfaces, not a preferred backend or the behavior of every tool release.
- **PyPA sdist and wheel format specifications** ([SRC-07](https://packaging.python.org/en/latest/specifications/source-distribution-format/), [SRC-08](https://packaging.python.org/en/latest/specifications/binary-distribution-format/)): current `/en/latest/` snapshots accessed 2026-11-06; describe standard archive structure and wheel tags, not a universal project-specific manifest or tested target matrix.
- **PyPA entry-points specification** ([SRC-13](https://packaging.python.org/en/latest/specifications/entry-points/)): current `/en/latest/` snapshot accessed 2026-11-06; documents installed entry-point metadata, not whether a specific project command works.
- **PyPA Dependency Groups specification** ([SRC-16](https://packaging.python.org/en/latest/specifications/dependency-groups/)): current `/en/latest/` snapshot accessed 2026-11-06; it states dependency groups are not included as distribution metadata. The page identifies PEP 735 approval in October 2024; tool-specific group-install behavior is outside this operation.
- **PyPA Version Specifiers specification** ([SRC-10](https://packaging.python.org/en/latest/specifications/version-specifiers/)): current `/en/latest/` snapshot accessed 2026-11-06; it defines version identifiers/comparison, not a project's API compatibility or release policy.
- **PyPA Packaging Flow and Overview** ([SRC-01](https://packaging.python.org/en/latest/flow/), [SRC-11](https://packaging.python.org/en/latest/overview/)): current `/en/latest/` snapshots accessed 2026-11-06; used only for lifecycle-stage and library/application distinctions, not a universal delivery method.
- **PyPA Tool Recommendations** ([SRC-17](https://packaging.python.org/en/latest/guides/tool-recommendations/)): current `/en/latest/` snapshot accessed 2026-11-06; it explicitly avoids blanket backend recommendations. Tool-specific fit remains a project decision.
- **PyPA `build` basic usage and explanation** ([Basic Usage](https://build.pypa.io/en/latest/how-to/basic-usage.html), [SRC-06: How it Works](https://build.pypa.io/en/latest/explanation/how-it-works.html)): both rendered pages identify `build` **1.6.1**, accessed 2026-11-06. Basic Usage documents `python -m build` as the default sdist-then-wheel-from-sdist workflow, `--sdist` and `--wheel` for one format, and wheel construction from an sdist input. These commands and defaults apply to this observed frontend version, not every frontend or target project.
- **PyPA Installing Packages guide** ([SRC-09](https://packaging.python.org/en/latest/tutorials/installing-packages/)): rendered pip documentation identifies **pip 27.0**, accessed 2026-11-06; it documents installation from local archives and wheel/sdist selection behavior. This does not establish the target installer/version or availability of dependencies.

These source checks authorize no real-project build and do not establish target-project versions. A generic workflow can be authored without selecting a real project or mandating any tool version. At task execution, inspect the target's existing frontend, backend, installer, and versions; use the documented `build` commands only when the target's `build` version matches the observed **1.6.1** evidence above. If a selected tool/version differs or its relevant behavior remains unknown, check only that target-version documentation when authorized; until verified, defer the affected action as non-executable and record the exact source/version needed. For installation, use the project's approved installer and report its actual version and tested targets; the pip 27.0 page observation is not a target-version assumption. No real-project build or installation was authorized or performed during authoring.

## Docs

Load only the passive topic needed for the current distribution request:

- `python-project-reference -> reference/distribution-artifacts.md` — packaging metadata, frontend/backend roles, formats, tags, contents, and install evidence.
- `python-project-reference -> reference/project-context-and-layout.md` — project kind, supported targets, and compatibility context.
- `python-project-reference -> reference/source-and-api.md` — public import, API, type, and version-compatibility promises.
- `python-project-reference -> reference/environment-and-dependencies.md` — dependency/environment ownership boundary.
- `python-project-reference -> reference/secure-configuration-and-data-handling.md` — sensitive data and artifact-content exposure.

The named documentation skill is passive context: loading it does not authorize effects or transfer validation/reporting ownership. This operation retains its own workflow, checks, and outcome evidence.
