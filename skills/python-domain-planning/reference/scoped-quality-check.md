# Scoped Quality Check

> **Authority boundary:** This is a passive workflow document. It describes a scoped
> practice for reference only; it is not an executable procedure or a source of
> execution authority.

`scoped-quality-check` - `python-quality-workflow` - Assess named paths or explicitly
requested quality configuration without source or test remediation.

**Use when:** A request asks for scoped Python checks/reports or standalone quality
configuration, with no production source or test remediation in the quality outcome.

## Purpose

The quality operation owns either a check-only report that preserves configuration
or an explicitly requested and authorized quality-configuration change with relevant
validation. Both cases default to non-writing diagnostics and exclude source/test
remediation.

## Descriptive Sequence

1. **Effective Settings And Requested Outcome** — Project kind, supported targets,
   effective configuration and precedence, tool versions, named paths, and environment
   establish the diagnostic scope. The request distinguishes check-only work from a
   configuration outcome; documented examples are not assumed to be enforced gates.
2. **Configuration Decision** — Check-only work leaves settings unchanged. A requested
   configuration outcome has separately authorized paths and a reviewable diff;
   existing settings and compatibility remain constraints outside that change. Missing
   tool dependencies or unrelated CI/script changes need a separate outcome rather
   than incidental installation or editing.
3. **Scoped Diagnostic Evidence** — Requested, authorized checks use the project's
   documented invocation and resolved version. For configuration changes, the actual
   configured tools assess the changed settings when available. Non-writing modes
   exclude source/test rewrites; cache, coverage, and report outputs still have explicit
   destinations and authorized effects. Universal commands or new CI gates are not
   inferred from the tool names.
4. **Interpretation And Report** — Exact invocations, versions, effective settings,
   targets, environment, write status, and results separate configuration errors,
   diagnostics, test failures, skips, and unavailable evidence. Coverage adds its source
   universe, test-file inclusion, exclusions, line/branch mode, configured threshold,
    and artifact. The report identifies findings for their owners without fixing them.

**Example handoff:** A check-only report states the exact command and tool version,
resolved config file, selected paths/target, environment, whether files/caches/reports
were written, findings, and unavailable checks. If a diagnostic identifies a production
bug, send it to the writer; if it identifies a standalone test gap, a test-only request
belongs to the test writer. Neither finding grants remediation authority. Coverage
percentages are comparable only with their source universe, branch mode, exclusions, and
report purpose stated.

For example, Ruff uses the closest configuration unless a child extends a parent, and
a file passed directly may still be analyzed despite an exclusion. Pyright has separate
configuration precedence and may analyze an excluded file imported by included code.
Coverage source selection, branch mode, and exclusions change the measured opportunities;
its percentage needs the source universe and report purpose. These mechanisms explain
unexpected diagnostics without authorizing fixes. For the detailed Ruff/Pyright and
coverage examples with publisher citations, explicitly load
`python-project-reference -> reference/static-quality.md` and
`python-project-reference -> reference/testing-and-coverage.md`.

## Artifacts

- Scoped diagnostic report with exact invocations, versions, targets, and results.
- A quality-configuration diff only for a requested and authorized configuration
  outcome; a check-only report confirms that settings were unchanged.
- Coverage report context when requested.

## Validation Context

- The actual checks run and their write status, not an unrun assumption.
- Comparable counts or trends only when version, config, target, paths, environment,
  and suppressions are disclosed.
- A clean static check is not runtime correctness; test execution does not prove
  assertion adequacy.

## Prerequisites

- An existing Python project with quality configuration or a requested quality outcome.
- Authorization for any write-producing check or configuration change.
- The requested paths, tools, and environment context.

## Notes

- A diagnostic invocation may write caches or reports even without editing source.
  Non-writing diagnostics therefore do not establish that the entire invocation has
  no side effects.
- Autofix, source formatting, suppression generation, and other source/test-writing
  modes are outside the quality action.
- Separately requested production remediation belongs to `python-project-writer`,
  including directly coupled regression tests. Independent test-only remediation
  belongs to `python-project-test-writer`, each under its own authorization.

## Operation Handoff

The consuming operation owns the imperative procedure and all execution decisions. It
translates this passive context into its own bounded steps and owns any tools, writes,
delegation, output, and completion validation. This document does not execute, call
tools, modify files, delegate work, load other skills transitively, grant authority, or
establish completion evidence. Any additional reference must be explicitly loaded by the
consuming operation.
