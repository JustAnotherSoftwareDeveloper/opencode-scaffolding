# JSON Output Conventions

Keep JSON results on stdout and human-readable diagnostics on stderr, matching the output contract used by Python and Node scripts.

- **stdout** — Emit machine-readable JSON with `printf`, for example: `printf '{"status":"ok","count":%d}\n' "${count}"`.
- **stderr** — All stderr output uses `printf '...' >&2` for human-readable diagnostic messages. Prefix errors with `Error:`, warnings with `Warning:`, and verbose info with `Info:`.
