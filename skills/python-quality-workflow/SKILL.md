---
name: python-quality-workflow
description: "Use when configuring Python quality tools or running scoped quality checks and reporting results without source or test remediation."
selection:
  role: owner
  tags:
    actions: [configure quality tools, run scoped checks, report quality results]
    inputs: [Python project configuration, scoped quality request]
    outputs: [quality configuration, scoped check report]
    topics: [Ruff, Pyright, pytest, coverage]
    environments: [Python application, Python service, Python package, Python library]
    constraints: [preserve project settings, no source or test remediation]
  use_when:
    - a request asks for standalone Python quality configuration or scoped checks/reports
  not_for:
    - a request asks to change production behavior or edit tests, fixtures, or helpers
    - a request asks only for general Python source conventions
    - a request concerns the repository's scripts/python/ automation workflow
class: operation
---

# Scoped Quality Workflow

Own one bounded standalone quality-configuration or scoped check/report outcome for a
Python application, service, package, or library. Own project inspection, decisions,
authorized quality-configuration effects, validation, interpretation, and reporting.
This operation never edits production source, tests, fixtures, or helpers to remediate
findings, including when such edits are requested alongside quality work.

## Normalize Input

Identify the target project, requested quality outcome, tools and paths in scope,
available project and policy context, requested report, and explicitly authorized
effects. A quality request may configure tools or request diagnostics from Ruff, Pyright,
pytest, or coverage; it does not imply permission to change files or run every tool.
Ask a focused question when the target, scope, requested effect, or authorization is
materially ambiguous. Do not infer permission from repository access or a nearby config.

If a request combines quality work with a distinct production or test edit, perform only
the independently authorized quality outcome. Keep the source change with
`python-project-writer -> #production-behavior-change-workflow` and test, fixture, or
helper changes with `python-project-test-writer -> #test-only-change-workflow`, each
under its own authorization. Do not make these edits or treat a quality finding as their
authorization. Keep `scripts/python/` procedures and settings local to that workflow.

## Procedure

1. **Inspect without changing the project.** Identify project kind and supported
   Python/platform targets. Read only the relevant project guidance and quality
   configuration. For each requested tool, determine the effective config source and
   precedence, existing command or CI entry point, installed version when available,
   target paths, import or test environment, and local-versus-CI context. For coverage,
   inspect source selection, test-file inclusion, exclusions, measurement mode, report
   artifact, and any threshold. Distinguish enforced checks from documented examples;
   do not generalize repository `scripts/python/` settings.

   Load passive reference context selectively:

   - `python-project-reference -> reference/static-quality.md` for Ruff/Pyright
     configuration, scope, and diagnostic limits.
   - `python-project-reference -> reference/testing-and-coverage.md` for pytest and
     coverage scope, denominator, exclusions, and interpretation.
   - `python-source-style-guide -> reference/python-source-style-guide.md` only when
     the requested outcome concerns source conventions, not merely because a formatter
     or style rule is involved.

   References supply context only. They do not select a project command, authorize an
   effect, validate a result, or transfer completion evidence.

2. **Decide the smallest requested outcome.** Preserve existing project configuration
   and compatibility promises first, then applicable approved local policy. Use a
   proposed family default only for a new or unconfigured project when the request
   permits a choice. Make conflicts and unresolved local policy visible; do not silently
   migrate brownfield settings.

   When selection is permitted, the nonbinding family proposal is a modest explicit
   Ruff lint profile (for example, `E` and `F`, with `I` only by deliberate choice),
   preview disabled absent an intentional trial, and no unreviewed `ALL`; Pyright
   `standard` with explicit project targets and paths when Pyright is selected; and
   pytest/coverage only where they fit the project. State coverage purpose and
   denominator; choose line or branch measurement for the requested report. No family-
   wide threshold or universal check sequence is established. These are proposed
   choices, not comparative quality findings or policy.

3. **Authorize effects before acting.** Default to non-writing diagnostics. Checks may
   create caches, coverage data, or report files; inspect configured/documented effects
   and destinations rather than assuming an invocation is read-only. Do not create or
   overwrite project artifacts unless the exact output is requested and separately
   authorized. Never choose an autofix, source formatter, suppression generator, or
   other source/test-writing mode as a quality action. Write only explicitly requested
   and separately authorized quality-configuration paths, and inspect that diff. Do not
   change dependencies, locks, source, tests, fixtures, helpers, or unrelated CI/scripts
   as incidental work. If a requested effect exceeds this boundary, stop that effect and
   report the separate owner or authorization needed.

4. **Run only the authorized scoped checks.** Use the project's documented invocation
   and resolved tool version; do not invent universal commands, flags, targets, or a
   CI gate. Check tool configuration or execute a diagnostic only when it is requested,
   authorized, and applicable. For a configuration change, review the diff and validate
   the requested settings with the actual configured tools when available. Record the
   exact invocation, tool/version (or unknown), effective config, target paths and
   environment, local/CI context, write status, output destinations, and actual result.

   For any concrete version-sensitive command syntax or tool behavior, record the exact
   source/document, applicable version, access context and date, and limits. Existing
   reference evidence does not establish the target project's installed version. If
   the necessary source, version, access, or authorization is unavailable, do not guess
   or execute that detail: identify it, mark it deferred and non-executable, name the
   needed source/version, and give a bounded separately authorized refresh handoff.
   A copied-source hash is not freshness evidence.

5. **Interpret only the evidence collected.** Distinguish tool/configuration errors,
   diagnostics, test failures, skipped checks, and unavailable or inconclusive results.
   Compare counts or trends only when version, config, target, paths, environment, and
   suppressions are comparable or differences are disclosed. For coverage, report the
   measured source universe/denominator, test-file inclusion, exclusions, line/branch
   mode, threshold if configured, and artifact. A clean static check is not runtime
   correctness; test execution does not prove assertion adequacy; coverage measures
   execution within its configured universe, not behavior quality.

6. **Report the outcome.** State the requested scope and decision; configuration paths
   changed or confirm none; exact invocations, versions, effective settings, targets,
   environment, and results; whether anything was written; coverage context when
   relevant; and failures, skips, deferrals, and remaining evidence gaps. Do not imply
   an unrun check passed or claim broader compatibility, security, policy approval, or
   quality effectiveness. Identify requested source/test remediation as a separate,
   unauthorized-by-this-operation outcome for its owner.

## Evidence Scope

The design basis is A_BASE (`.analysis/1793895766484-python-enterprise-quality-baseline-analysis.md`) and A_MAP (`.analysis/1793896454804-python-enterprise-module-allocation-analysis.md`). Claim identifiers STATIC C01-C08, SQ C01-C08, TEST2 C01-C08, and TQ C01-C12 identify the supplied static-quality and testing/coverage evidence. Local claim/source navigation is recorded in `.research/20261105-rs01-python-enterprise-static-quality-standards/claims.md`, `.research/20261105-rs01-python-enterprise-static-quality-standards/sources.md`, `.research/20261105-6f2a9c-python-enterprise-testing-coverage-standards/claims.md`, `.research/20261105-6f2a9c-python-enterprise-testing-coverage-standards/sources.md`, `.research/20261104-185507-python-static-quality/claims.md`, `.research/20261104-185507-python-static-quality/sources.md`, `.research/20261104-cbf6ed2e-python-testing-quality/claims.md`, and `.research/20261104-cbf6ed2e-python-testing-quality/sources.md`. These sources support documented mechanics and scoped proposed choices; they do not establish comparative outcomes, user demand, universal thresholds, enterprise policy, or topology effectiveness. The detailed version, access-date, and qualification records remain in the selectively loaded references; they are not evidence of a target project's versions or configuration.

Existing source/version records read from the local references on 2026-11-06 (not
re-fetched for this authoring task) identify these publisher documents:

- Ruff 0.17.3: [linter](https://github.com/astral-sh/ruff/blob/0.17.3/docs/linter.md),
  [formatter](https://github.com/astral-sh/ruff/blob/0.17.3/docs/formatter.md),
  [configuration](https://github.com/astral-sh/ruff/blob/0.17.3/docs/configuration.md),
  and [preview](https://github.com/astral-sh/ruff/blob/0.17.3/docs/preview.md).
- Pyright 1.1.414: [configuration](https://github.com/microsoft/pyright/blob/1.1.414/docs/configuration.md),
  [import resolution](https://github.com/microsoft/pyright/blob/1.1.414/docs/import-resolution.md),
  and [typed libraries](https://github.com/microsoft/pyright/blob/1.1.414/docs/typed-libraries.md).
- Pytest 9.2.0: [fixtures](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/how-to/fixtures.rst),
  [parametrization](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/how-to/parametrize.rst),
  and [reference](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/reference/reference.rst).
- Coverage.py 7.17.2: [source selection](https://coverage.readthedocs.io/en/7.17.2/source.html),
  [branch measurement](https://coverage.readthedocs.io/en/7.17.2/branch.html),
  [exclusions](https://coverage.readthedocs.io/en/7.17.2/excluding.html), and
  [configuration](https://coverage.readthedocs.io/en/7.17.2/config.html).

The local records state these task-bounded primary-source checks were accessed 2026-11-06.
They support only those version-specific mechanics, not any target project's installed
versions, effective settings, paths, or environment. Original access context and limits
are recorded in `python-project-reference -> reference/static-quality.md` and
`python-project-reference -> reference/testing-and-coverage.md`; mutable stable/latest
pages and historical snapshots are not freshness evidence.

## Self-Validation

- The request is a standalone, bounded quality configuration or check/report outcome.
- Actual project configuration, targets, environment, and requested scope were inspected
  before deciding what to run or change.
- Existing settings and compatibility take precedence; proposed defaults are qualified
  and used only when a choice is allowed.
- Diagnostics are non-writing by default; any write is limited to explicitly authorized
  quality configuration, with no source or test remediation.
- Every executed check and its version, scope, write status, result, and limitations are
  reported; coverage includes its denominator and material measurement context.
- Version-sensitive details have permitted source/version/date/limits evidence or are
  explicitly deferred with a bounded authorized refresh handoff.
- Passive references add no authority or completion evidence; separate edits remain with
  their respective owners under separate authorization.
- The report distinguishes passed, failed, skipped, unavailable, and deferred work and
  claims no untested outcome or universal policy.
- Filled content uses semantic prose forms and contains no Markdown tables.

## Docs

Load only the relevant passive reference module:

- `python-project-reference -> reference/static-quality.md`
- `python-project-reference -> reference/testing-and-coverage.md`
- `python-source-style-guide -> reference/python-source-style-guide.md` only for a
  requested source-conventions outcome.

## Expected Output

One scoped quality configuration or check/report outcome with project context, actual
settings and targets, exact checks and results, write status, and coverage details when
applicable. If scope, authorization, or required version evidence blocks an effect,
make no unauthorized change or guessed invocation; report the specific blocker and
bounded next step.
