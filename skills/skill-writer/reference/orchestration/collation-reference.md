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
  `success`: all items succeeded.
  `partial`: some items failed.
  `failure`: all items failed.
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

Orchestrated skills use this structure when collating worker results.
The orchestrator sets `status` based on worker outcomes.
It populates `source_tags` from worker or deployment tags.
It collects worker outputs into `items`.

## Cross-References

- `../authoring/frontmatter-rules.md` — Class taxonomy and frontmatter rules.
- `../platform/platform-context.md` — Platform context.
- `./orchestrated-usage.md` — Collation note with usage context.

> Keep the canonical collation definition in this file. Do not reintroduce it in REFERENCE.md.