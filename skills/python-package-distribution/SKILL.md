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

Change requested distribution metadata/build configuration, produce promised wheels
or source distributions (sdists), and check their contents and installation. Python
code or `pyproject.toml` alone does not establish a distribution need. Uploading,
registry administration, and full application deployment are separate lifecycle stages.

## Normalize Input

Identify the project/root, metadata/configuration changes, artifact set/output location,
supported Python/platform/runtime targets and tags, expected contents/entry points,
clean-install targets, and authorized configuration, build, install, and temporary-
environment effects. Ask if distribution applicability or required promises are unclear;
block writes/builds without project scope or authorization. An unspecified non-blocking
target defers only its affected check, never counts as a pass.

## Procedure

1. **Inspect the delivery contract.** Confirm that the consumer needs a distribution;
   record only requested artifacts, not customary extra wheels, sdists, tags, CLIs, or
   metadata. Read packaging configuration and release guidance for frontend/backend,
   static/generated version source, metadata, file selection, names/tags, targets,
   imports, and entry points. Preserve configuration and compatibility/release promises
   first, approved local policy next, and proposed defaults only for new or unconfigured
   projects when choice is allowed. Surface conflicts; keep `scripts/python/` practices
   local rather than treating them as packaging policy.
2. **Verify applicable syntax and behavior.** Use permitted target-tool/version
   documentation and relevant context under Docs. Obtain separate scoped authorization
   before checking current external primary sources. Record exact source, applicable
   version, access context/date, and limits; mutable snapshots do not establish target
   versions or freshness. If evidence, access, or authorization is missing, name the
   affected detail and needed source/version, defer it as non-executable, and give a
   bounded authorized refresh handoff. Do not install or upgrade tools without permission.
3. **Make requested metadata/configuration changes.** Preserve the selected backend,
   frontend, and version source unless an authorized change addresses them. Where
   standardized `[project]` metadata applies, check name, static/backend-provided
   version, `requires-python`, runtime requirements/extras, readme/license, and promised
   entry points against the applicable specification and project contract. Internal
   dependency groups are not published requirements/extras. Do not choose API/release
   policy, migrate metadata models incidentally, or take on dependency/environment changes.
4. **Build the promised artifacts.** Use the authorized frontend and output location;
   do not overwrite or delete existing artifacts without permission. Select formats
   explicitly when needed: frontend defaults may produce multiple artifacts or build
   a wheel from an intermediate sdist. Consult the local build/install reference for the
   version-qualified `build` example, not a universal invocation. If the needed tool
   is unavailable and installation is unauthorized, stop that action and report it.
5. **Inspect actual contents.** Record filenames, artifact types, metadata versions
   where available, and wheel Python/ABI/platform tags. Check wheel install layout and
   metadata, sdist standard structure and project-specific source/build inputs, and
   relevant unintended/sensitive files against promised contents, inclusion rules,
   metadata, and supported targets. A successful build, filename, tag, or listing alone
   proves neither installability nor the full support matrix.
6. **Check clean installations.** For each requested target/artifact, install the exact
   local wheel in a fresh target-appropriate environment with the approved installer;
   test a promised sdist by building/installing from that archive as relevant. The
   checkout/developer environment cannot be the sole evidence. Exercise promised
   imports, extras, and installed entry points. Record Python/platform, installer and
   backend/frontend versions, exact commands, dependency/index constraints, and results.
   Do not change declarations to work around install failures; report them for a
   separate dependency decision.

## Self-Validation

- Actual metadata, artifacts, and temporary-environment effects match authorization.
- Every promised artifact/target has content and clean-install evidence or an explicit
  failed, deferred, or untested status; local success implies no reproducibility,
  universal compatibility, policy approval, upload, or deployment result.

## Expected Output

Return requested changes and artifacts with a concise report of paths/names/tags,
metadata/content findings, exact tools/versions/commands, clean-install results by
target, all effects, and the tested subset of promised support. Distinguish failures,
deferrals, and untested scope; state blockers and bounded next steps rather than
presenting incomplete validation as success.

## Docs

- [Metadata, build, and install](reference/metadata-build-and-install.md) — packaging
  configuration, artifact inspection, and consumer-install checks.

Explicitly load `python-project-reference` before reading a relevant module below.
Its passive context grants no effects, policy, or completion evidence.

- `python-project-reference -> reference/distribution-artifacts.md` — metadata,
  frontend/backend roles, formats, tags, contents, and installation evidence.
- `python-project-reference -> reference/project-context-and-layout.md` — supported targets.
- `python-project-reference -> reference/source-and-api.md` — import/API/type promises.
- `python-project-reference -> reference/environment-and-dependencies.md` — dependency boundary.
- `python-project-reference -> reference/secure-configuration-and-data-handling.md` —
  sensitive artifact contents.
