# Library Distribution

> **Authority boundary:** This is a passive workflow document. It describes a scoped
> practice for reference only; it is not an executable procedure or a source of
> execution authority.

`library-distribution` - `python-package-distribution` - Prepare and validate promised
wheel and sdist artifacts for a distributable library.

**Use when:** A request asks for Python distribution metadata, build configuration,
wheel or sdist artifacts, artifact contents, or installability checks for a reusable
library or installable CLI.

## Purpose

`python-package-distribution` owns the requested metadata, build configuration,
artifact contents, and install evidence. The practice distinguishes a working checkout
from a usable consumer artifact; it includes neither registry upload nor deployment.

## Descriptive Sequence

1. **Delivery Contract** — The requested artifact set, existing frontend/backend,
   metadata/version source, supported targets, wheel tags, and expected files define
   the consumer promise. A metadata-only request does not imply a build or install;
   an application without an installable delivery need does not imply a wheel.
2. **Metadata And Build Choices** — Authorized changes preserve the selected build
   system and version source unless their change is explicitly in scope. Field meaning
   rests on the applicable specification and actual project contract, including promised
   entry points, resources, and package contents rather than common but unnecessary fields.
3. **Artifact Inspection** — Requested builds yield wheel and/or sdist archives whose
   filenames, tags, metadata, and contents can be compared with the delivery contract.
   A missing module or resource is an artifact finding even if checkout tests import
   the source successfully.
4. **Consumer Installation Evidence** — A clean, target-appropriate wheel install
   provides import and entry-point evidence without checkout-path masking. Sdist
    build/install evidence covers that route only where promised. Exact tool versions,
    commands, targets, and unresolved failures delimit the installability claim.

**Example handoff:** The distribution report names the requested wheel/sdist, backend
and frontend versions, artifact tags and inspected files, then records clean install and
import/entry-point results for promised targets. A checkout import or editable install
does not substitute for the regular consumer path; an sdist failure is not permission to
change dependency declarations. Distinguish the frontend that invokes a build from the
backend named in `[build-system]`; isolated build requirements are not the consumer
runtime environment. Building a wheel from the sdist can reveal files omitted from the
source archive. Inspect package discovery, resources, entry points, metadata, and tags
against the actual consumer promise: an artifact tag is a compatibility claim, not proof
that the target was tested. For a worked build/install diagnosis and direct PyPA/tool
citations, explicitly load
`python-project-reference -> reference/distribution-artifacts.md`.

## Artifacts

- Distribution metadata or build configuration changes.
- Requested wheel and/or sdist archives with recorded names, tags, and contents.
- Clean install evidence by target, including any entry-point or import checks.

## Validation Context

- Artifact filenames, tags, metadata, and content inspection results.
- Clean wheel install and promised sdist build/install outcomes, with skipped or
  unavailable targets distinguished from successful ones.
- Exact frontend/backend versions, installer, and tested environment.

## Prerequisites

- A distributable library or installable CLI with a documented delivery need.
- Authorization for metadata/configuration changes and build/install effects.
- Existing frontend/backend, version source, and supported-target context.

## Notes

- Common artifacts, tags, and metadata fields are not implicit requirements.
- A failed install can require a separate dependency decision; it does not authorize
  distribution work to change dependency declarations as a workaround.
- One local build does not prove the full target matrix or deployment readiness.
- Publishing, upload authority, provenance policy, and deployment remain outside this
  workflow.

## Operation Handoff

The consuming operation owns the imperative procedure and all execution decisions. It
translates this passive context into its own bounded steps and owns any tools, writes,
delegation, output, and completion validation. This document does not execute, call
tools, modify files, delegate work, load other skills transitively, grant authority, or
establish completion evidence. Any additional reference must be explicitly loaded by the
consuming operation.
