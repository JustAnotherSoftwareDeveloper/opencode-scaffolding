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

Configure Python quality tools or run scoped checks and report their results. Never
remediate production source, tests, fixtures, or helpers, even in a mixed request;
those changes require their own operation and authorization.

## Normalize Input

Identify the project, requested configuration or diagnostic outcome, tools, paths,
policy context, report, and authorized effects. A request involving Ruff, Pyright,
pytest, or coverage does not authorize every tool or a write. Ask if scope or permission
is materially ambiguous; repository access grants neither. Isolate the independently
authorized quality part of mixed requests. Keep `scripts/python/` procedures and
settings local to that workflow.

## Procedure

1. **Inspect effective settings.** Identify project kind and Python/platform targets.
   For each requested tool, inspect configuration sources/precedence, documented
   command or CI entry point, installed version, paths, import/test environment, and
   local/CI context. Distinguish enforced checks from examples. For coverage, inspect
   source selection, test-file inclusion, exclusions, mode, report artifact, and threshold.
2. **Choose the requested settings or checks.** Preserve existing configuration and
   compatibility first, approved local policy next, and proposed defaults only for a
   new or unconfigured project when choice is allowed. Surface conflicts rather than
   silently migrating settings.

   The nonbinding family proposal is explicit, modest Ruff rules (for example `E`/`F`,
   `I` by deliberate choice), preview off except for an intentional trial, and no
   unreviewed `ALL`; Pyright `standard` with explicit targets/paths; pytest/coverage
   only where suitable. State coverage purpose, denominator, and line/branch choice.
   These are proposed choices, not comparative findings, a universal sequence, or a
   family-wide threshold.
3. **Confirm all effects.** Default to non-writing diagnostics, but inspect cache,
   coverage-data, and report destinations. Creating or overwriting project artifacts
   requires the exact output to be requested and separately authorized. Write only
   requested, separately authorized quality configuration; never use autofix,
   source-formatting, suppression-generation, or other source/test-writing modes.
   Do not incidentally change dependencies, locks, or unrelated CI/scripts. Stop
   out-of-scope effects and name the owner or authorization needed.
4. **Verify syntax and tool behavior.** Use permitted target-project documentation and
   resolved versions; reference examples do not establish installed versions. Obtain
   separate scoped authorization before checking current external primary sources.
   Record exact source, applicable version, access context/date, and limits; hashes
   do not prove freshness. If evidence, access, or authorization is missing, name the
   affected detail and needed source/version, defer it as non-executable, and give a
   bounded authorized refresh handoff.
5. **Run and record scoped checks.** Use configured commands and targets, not invented
   flags or a universal CI gate. For configuration changes, review the diff and validate
   settings with the actual tools when available. Record exact invocation, version
   (or unknown), effective config, paths/environment, local/CI context, write status,
   destinations, and result.
6. **Interpret results within scope.** Separate tool/config errors, diagnostics, and
   test failures from skips, unavailable, deferred, or inconclusive work. Compare
   counts/trends only with comparable versions, configuration, targets, paths,
   environment, and suppressions, or disclose differences. Coverage results need their
   measured source universe/denominator, test inclusion, exclusions, line/branch mode,
   configured threshold, and artifact. Static checks do not prove runtime correctness;
   tests do not prove assertion adequacy; coverage measures execution, not behavior quality.

## Self-Validation

- The diff and command effects contain no source/test remediation or unauthorized writes.
- Conclusions match actual tool scope and disclosed comparison/coverage context, without
  implying unrun checks, broader compatibility/security, or policy approval.

## Expected Output

Return requested configuration changes, if any, and a scoped report of decisions,
changed paths, exact check evidence, write effects/destinations, coverage context,
and failures or gaps. State any blocker and bounded next step. Identify source/test
remediation for its separate owner rather than performing it.

## Docs

- [Configuration and diagnostics](reference/configuration-and-diagnostics.md) — effective
  settings, diagnostic examples, and incremental adoption.

Explicitly load the named documentation skill before reading a relevant module below.
References supply context, not project commands, permissions, or completion evidence.

- `python-project-reference -> reference/static-quality.md` — Ruff/Pyright configuration
  and diagnostic limits.
- `python-project-reference -> reference/testing-and-coverage.md` — test/coverage scope
  and interpretation.
- `python-source-style-guide -> reference/python-source-style-guide.md` — only for a
  requested source-conventions outcome, not every formatter/style-rule request.
