# Generic Executor Reference

`generic-executor` is the default operation for one bounded task when no specialized
operation clearly owns the result. It is a semantic fallback, not a failure fallback.

Use a specialized operation when the task depends on that operation's distinct
lifecycle, artifact contract, orchestration flow, destructive authority, or other
special execution semantics. Otherwise use `generic-executor`, optionally alongside
materially relevant documentation skills.

A missing specialized match is normal and should not block. Collection failure, an
absent or stale collector record, class/path mismatch, failed required skill load, or
malformed task contract remains a hard failure and must not be hidden by fallback.

Generic execution may cover source code, tests, scripts, configuration,
documentation, fixtures, analysis, and other bounded repository work. Follow the
canonical task packet and worker resource-flexibility rules rather than maintaining a
second private input grammar. Documentation skills are passive guidance and do not
grant authority.
