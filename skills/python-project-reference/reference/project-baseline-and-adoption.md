# Project Baseline And Incremental Adoption

This is a nonbinding starting point for ordinary applications, services, internal
packages, and libraries. It preserves the useful choices and adoption guidance from
the family's baseline analysis without treating that proposal as approved policy.

## Precedence And Applicability

Existing project configuration and compatibility promises come first, applicable
approved local policy second. Proposed defaults apply only to new or unconfigured
projects when the request permits choosing. A conflict needs an explicit owner
decision, not a silent migration. Repository `scripts/python/` settings remain local.

The choices below are engineering judgments informed by documented mechanisms. They
have not been compared across a representative project set. Public documentation
does not supply an organization's support matrix, service budgets, or security policy.

## Proposed Starting Choices

### Delivery, Layout, And Support

- Declare actual Python support separately from the locally requested interpreter;
  report which Python/platform combinations were tested.
- For a new distributable library, `src/` plus external tests is a useful starting
  layout. Keep a service's tree aligned with its framework and real entry points;
  there is no universal application layer tree.
- Keep source-style choices with the explicitly loaded
  `python-source-style-guide -> reference/python-source-style-guide.md`, rather than
  duplicating naming, docstring, and annotation rules here.

See [Project Context And Layout](project-context-and-layout.md) for the import-path
trade-off and [Distribution Artifacts](distribution-artifacts.md) for consumer installs.

### Environments And Dependencies

Where a manager choice is allowed, uv is the proposed starting option: declarations
in `pyproject.toml`, committed `uv.lock`, ignored/uncommitted project `.venv`, and
project commands through `uv run`. CI would select the intended interpreter, groups,
and extras and reject a stale lock rather than rewrite it. Preserve Poetry, pip-tools,
Conda, or another working manager in an established project; no superiority finding
supports a migration merely to match this proposal.

A dependency needs a named capability or constraint not adequately met by the standard
library, existing code, or an approved package. Compare fit, supported targets,
maintenance/security response, source authenticity, direct/transitive footprint,
build/install behavior, and license evidence. Record no-add/add/replace/defer and the
remaining risks. For an existing package, focus reevaluation on material version,
support, vulnerability, or compatibility changes rather than auditing the whole graph
on every edit. Scores and popularity are investigation leads, not verdicts.

See [Environment And Dependencies](environment-and-dependencies.md) for category,
interpreter, lock, and installed-state distinctions and version-qualified uv examples.

### Static Quality

For an unconfigured project selecting Ruff, the proposal is lint plus formatting,
an explicit `E`, `F`, `I` lint profile, and preview off unless deliberately trialed.
`I` is an intentional import-sorting choice, not formatter behavior. Do not choose
`ALL` by default. Non-writing lint/format checks suit a diagnostic or CI outcome;
autofix and formatting writes require the source-change owner's scope.

Where Pyright is selected, the proposal starts at `standard` with explicit source
paths, Python/platform targets, and the dependency environment. Strict scopes are a
deliberate increment, not a default migration of every existing module. Resolve import
and configuration errors before interpreting an apparent clean result. `--verifytypes`
is a separate completeness measure for a declared typed library, not app annotation
coverage. See [Static Quality](static-quality.md) for mechanics and diagnostic limits.

### Behavior Tests And Coverage

Pytest is a proposed choice where it fits; established frameworks remain valid.
Important cases make the behavior-changing act and observable assertion clear. Fixtures,
parametrization, and cleanup should clarify cases rather than impose a test taxonomy.

The proposed primary coverage report includes maintained production modules in selected
packages, including eligible unexecuted modules. Tests may be measured separately or
included when the report's purpose calls for it. This differs from coverage.py's own
recommendation to include tests; it is a report-purpose choice, not tool guidance.
Line measurement is a starting point; branch mode is useful where alternate control
flow matters. No family-wide percentage is established.

One proposed local review criterion is a named test for each changed production
behavior and cases for relevant outcomes of meaningful changed branches. It is not an
externally validated effectiveness metric or an automatic CI gate. A report needs
source set, exclusions, mode, threshold if any, and collected targets before a trend
is interpretable. See [Testing And Coverage](testing-and-coverage.md).

### Public Contracts And Distribution

For a new library, document supported imports, calls, side effects, failure outcomes,
and subclass behavior where promised. State runtime/platform and typed-client support
separately. One possible local release-policy choice is SemVer-compatible meanings,
migration guidance and warnings, retaining a deprecated public path through at least
the next minor release before major-release removal, with documented urgent/security
exceptions. This is only the baseline's proposed example: CPython and other maintainers
have different policies, and PEP 440 version syntax imposes none of these promises.

Compatibility evidence can exercise representative old import/call/error patterns and
selected typed-client expectations on declared targets. A hidden deprecation warning
or skipped interpreter is not evidence that consumers observed or passed that check.
See [Source And API](source-and-api.md), [PEP 387](https://peps.python.org/pep-0387/),
[Python warning filters](https://docs.python.org/3.15/library/warnings.html#warning-categories),
and [PyPA versioning](https://packaging.python.org/en/latest/discussions/versioning/).

Build distributions only for an actual installable delivery promise. If both wheel
and sdist are promised, content inspection, clean wheel installation, and a build/
install path from the sdist provide distinct evidence. Preserve the backend, version
source, artifact set, tags, and release path in existing projects. One local build is
not a full support matrix, publication, provenance verification, or deployment result.
See [Distribution Artifacts](distribution-artifacts.md).

### Failure, Security, Logging, And Concurrency

- **Failure contracts:** catch to recover, translate, or deliberately suppress;
  preserve causes on translation and pair resources with cleanup. For new service
  request paths, the proposal is finite timeouts at outbound blocking/network calls
  and one monotonic request budget where client APIs support it. Numbers require a
  latency/SLO decision. No generic retry is proposed: replay safety or known
  non-application comes first, followed by bounded attempts/backoff and explicit
  outcome handling. Avoid stacked opaque retries across SDKs, application, proxies,
  and workers. See [Source And API](source-and-api.md).
- **Security:** required security-critical settings should fail safely when missing or
  invalid rather than use known/empty production credentials. Keep debug detail off in
  production and secrets out of source, fixtures, output, and artifacts. Non-production
  sentinel tests can check specific log/error/representation/serialization/artifact
  paths; masking one representation proves nothing about another. Delivery channels
  depend on deployment exposure. See [Secure Configuration And Data Handling](secure-configuration-and-data-handling.md).
- **Logging:** a new service may choose structured fields for event, severity,
  operation/outcome, timestamp, and a scoped interaction ID where useful. Module loggers
  leave application entry points in charge of handlers; libraries do not take over
  consumer output. Select bounded fields, not whole requests or unchecked exception
  text. Representative tests can check expected fields, correlation where selected,
  duplicates, secret sentinels, and unsafe newlines at actual output boundaries. No
  exporter adoption is implied. See [Logging And Observability](logging-and-observability.md)
  and [OWASP logging guidance](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html).
- **Concurrency:** preserve synchronous code absent a workload/interface need. Related
  async children may use TaskGroup when sibling cancellation fits; offload blocking I/O
  from an event loop and consider CPU parallelism only with runtime/cost evidence.
  Performance claims need representative before/after measurements. Failure,
  cancellation, cleanup, backpressure, and shutdown tests address separate lifecycle
  promises. See [Async And Concurrency](async-and-concurrency.md).

## Low-Disruption Adoption

An established project can adopt selected improvements without replacing its toolchain:

- **Inventory:** project kind, support and API promises, manager/lock/groups, effective
  quality configs/versions, test collection, coverage denominator/exclusions/gates, CI
  commands, effective config sources, log routing, and concurrency model. Distinguish
  enforced checks from documentation examples.
- **Diagnose:** existing commands/settings establish a baseline of diagnostics, test
  outcomes, report artifacts, skips, and actual runtime targets. Missing checks remain
  missing, not passed.
- **Bound regression review:** preserve project-wide thresholds; identify new findings
  attributable to changed code. Add tests around changed behavior first. A coverage
  ratchet needs the same source universe and mode; widening the denominator is not a
  like-for-like regression.
- **Tighten selected scopes:** reviewed Ruff rule batches, deliberately chosen import
  sorting, selected stricter type-check scopes, branch reports where useful, and stale
  suppression removal avoid blanket `ALL`, ignores, or generated `noqa` shortcuts.
- **Adopt runtime controls at real boundaries:** client timeout scopes and replay
  contracts precede retries; safe effective settings/output precede secret-channel
  changes; a measured bottleneck and lifecycle contract precede concurrency refactoring.
- **Record exceptions:** another manager, framework, schema, version scheme, or execution
  model may remain appropriate. Urgent/security changes can justify a faster path when
  user impact, exception scope, and migration evidence are explicit.

Comparable trends require the same versions, configuration, targets, environment,
paths, exclusions, and output mode, or disclosed differences. Lower diagnostic counts
and higher percentages alone are not quality improvements.

## Decisions Still Needed Locally

Support matrix; API/deprecation promises; CI enforcement; dependency/license/security
review; data classification and privacy obligations; approved secret identities/stores;
SLOs and timeout/deadline budgets; retry ownership and idempotency protocol; log schema,
access and retention; concurrency, admission, queue, and shutdown limits all need local
owners. No universal coverage target, timeout, retry count, rotation period, or pool
size follows from this reference.

## Topic Boundaries

The linked chapters explain the mechanisms, worked cases, and source qualifications
behind these choices. Tool documentation does not establish optimal organizational
defaults; support, performance, and security claims still need project-specific evidence.

The nine domain chapters remain the technical homes. General exception, cleanup,
deadline, and replay contracts belong to Source And API; cancellation/task/executor
mechanics belong to Async And Concurrency. Security decides which values may be
exposed; logging explains record representation/routing; distribution explains artifact
contents and installation. A shared filename such as `pyproject.toml` does not merge
these outcomes. For operation selection and sequencing, explicitly load
`python-domain-planning -> #common-workflows`.
