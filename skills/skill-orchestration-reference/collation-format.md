# Collation Output Structure

Default collation format for orchestrated skills aggregating results from multiple workers.

## Default Format

JSON.
Universally parseable, extensible, and supports nested structures.

Alternatives considered — plaintext (rejected: not extensible, hard to parse programmatically).
JSON with schema validation deferred (can add later without breaking the shape).

## Top-Level Shape

```json
{
  "status": "success | partial | failure",
  "source_tags": ["<<tag-1>>", "<<tag-2>>"],
  "items": ["<<item-1>>", "<<item-2>>"]
}
```

- **`status`** — Overall collation result.
  `success`: every delegated worker returned `COMPLETE`.
  `partial`: at least one worker returned `PARTIAL`, or a mix of usable and `BLOCKED` results exists.
  `failure`: no usable payload exists because every worker returned `BLOCKED`.
- **`source_tags`** — Array of tag strings identifying which workers or phases produced the items.
  Tags follow `kebab-case` convention.
- **`items`** — Array of item objects.
  Item shape is defined by each collation unit, not constrained by the top-level schema.

## Item Shape

Each collation unit defines its own item structure.
Items are heterogeneous within a single collation.

Examples:

- Finding items: `{file, line, severity, message}`
- Verification items: `{check, passed, detail}`
- Task items: `{id, purpose, status, output}`

## Usage

Use this structure when collating worker results.
Validate each worker result envelope before collation.
Set `status` from the envelope-status mapping above.
Populate `source_tags` from worker or deployment tags.
Collect validated `Deliverable` payloads into `items`.
Exclude `None` payloads from `BLOCKED` results and retain their blocker details in the orchestrator's diagnostics.

## Cross-References

- `./orchestrated-worker-patterns.md` — Worker pattern contracts and output requirements.
- `./orchestration-usage.md` — Collation note with usage context.

> Keep the canonical collation definition in this file. Do not reintroduce it in other files.
