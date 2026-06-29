# JSON Output Conventions

Follow the same output contract as Python and Node scripts.

- **stdout** — Machine-readable JSON output.
  Use `printf` for JSON emission: `printf '{"status":"ok","count":%d}\n' "${count}"`.
- **stderr** — Human-readable diagnostic messages.
  Prefix errors with `Error:`, warnings with `Warning:`, verbose info with `Info:`.
  All stderr output uses `printf '...' >&2`.