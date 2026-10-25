# Research Artifacts

## Bundle Location And Collision Handling

For every completed request, create one bundle at repository-root `.research/<unique-run-id>-<task-slug>/`. Treat the run ID and task slug as single filename components, not paths. Keep every artifact created by this operation inside that bundle. The bundle is durable on disk; this contract makes no claim that it is tracked, committed, ignored, or retained for a particular period.

## Safe Path Construction And Containment

1. Derive a task slug from task text by lowercasing it, replacing each maximal run of characters outside ASCII `a`–`z` and `0`–`9` with one hyphen, and trimming leading or trailing hyphens. If the result is empty, stop and report that a safe task slug cannot be formed. If an explicit slug is supplied, accept it only when it already matches `^[a-z0-9]+(?:-[a-z0-9]+)*$`; reject rather than repair a path-like explicit slug. Generate the unique run ID using only lowercase ASCII letters, digits, and single hyphen separators, and require it to match the same pattern. Never use raw user text, a supplied path, or an unchecked identifier as a path component.
2. Resolve the repository root to its canonical absolute path. `.research` must be that root's direct child, a real directory, and not a symbolic link. If it does not exist, create it without following or replacing an existing path, then check it again. Stop if it is a symlink, is not a directory, or resolves anywhere other than `<canonical-repository-root>/.research`.
3. Build the bundle path only by joining the canonical `.research` directory with the validated `<unique-run-id>-<task-slug>` basename. Inspect existing components without following symlinks. An existing bundle path is a collision; do not merge with it, follow it, overwrite it, or write elsewhere. Resolve the prospective destination from its existing parent and require it to be strictly inside the canonical `.research` directory, using path-component containment rather than a string-prefix comparison.
4. Create the bundle directory exclusively, so creation fails if any path already exists. Recheck without following symlinks and resolve the created directory; require it to be a real directory strictly beneath canonical `.research`. Create each fixed artifact filename below only if absent, without following symlinks or replacing an existing path, and verify its resolved parent remains the bundle directory. If the available filesystem operation cannot provide these no-replace and no-follow checks, stop and report persistence failure rather than writing to an unchecked path.

These checks reject separators and traversal syntax in explicit slugs, prevent a symlinked `.research` or bundle path from redirecting output, and keep resolved artifact paths inside repository-root `.research`. Do not create research artifacts elsewhere.

Check the destination before writing and create it without replacing existing paths. If the destination already exists or cannot be created safely, do not overwrite, merge, or write elsewhere; stop and report that persistence failed. A later attempt may use a new run identifier. Do not alter `.gitignore`, repository tracking, retention settings, or existing `.research` content.

## Required Files And Fields

Each completed bundle contains these four Markdown files:

- `README.md` — `Question`; `Intended use`; `Scope and time boundary`; `Created at` using an observed timestamp or `unavailable`; `Bundle status` (`complete` only after verification); and links to the three records below.
- `answer.md` — `Question`; `Scope`; `Answer or findings`; `Interpretation`; `Uncertainty and limitations`; and the claim IDs supporting material statements.
- `sources.md` — a search-attempt log and source register. For every attempt, record attempt ID/order, tool name, query, route reason, outcome, and visible result count if supplied. For every used source, record source ID, title, URL, discovery tool, publication date and author only when surfaced, page-reading tool, and inspected passage/location. Mark unavailable fields explicitly; do not infer provider identity or timestamps.
- `claims.md` — for each material claim, record claim ID and wording; whether it is source-reported or an interpretation; supporting source IDs and inspected passages/locations; contrary or qualifying source IDs and passages when present; and task-specific fit and limitations.

Keep source IDs and claim IDs stable across the bundle. The answer and claim record must agree, and every cited source ID must resolve to an entry in `sources.md`.

## Completion And Failure

Verify that all four files are readable, every required field is present, internal IDs and links resolve, and the complete answer and claim support are saved. Do not mark the bundle complete until these checks pass. If any file cannot be persisted or verified, report the request as incomplete; do not claim a completed answer merely because text was returned in the session. Never silently replace an existing bundle or put research output in another workspace.
