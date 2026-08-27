# Implementation Steps Format

A structured format for documenting implementation steps using Markdown headers,
subheaders, and 1-2 sentence bullets with selective bolding. Boundary meaning comes
from the shared [task-contract atomicity and alignment reference](../../task-contract/reference/atomicity-and-alignment.md);
this file owns only the presentation format.

## Format Structure

The format uses a three-level Markdown hierarchy:

- **H2 Header**: Change category that groups related atomic changes, such as
  `## Authentication Refactoring`.
- **H3 Subheader**: Specific drafted task result, such as
  `### Add \`auth.provider\` to \`config.yaml\``.
- **Bullets**: Details in 1-2 sentences with selective bolding, such as
  `- **What**: ...`.

## Format Rules

1. **One H3 per drafted task result** — Each H3 subheader represents one change
   boundary as reviewed against the shared task contract.
2. **H2 groups parallel-capable steps** — Multiple H3s under one H2 may be executed in parallel
3. **Bullets are 1-2 sentences** — Concise but complete; no truncation
4. **Selective bolding** — Bold key elements: file paths, reasons, impacts, and the "What" component
5. **All steps self-contained** — Each step includes What, Where, and Why (impact optional)

## Complete Example

```markdown
## Authentication Refactoring

### Add `auth.provider` configuration field to `config.yaml`

- **What**: Introduce a new `auth.provider` field to support multiple authentication backends (e.g., `local`, `ldap`, `oauth2`).
- **Where**: `config.yaml` — add as a top-level field at line 12.
- **Why**: Current implementation hardcodes the local auth backend; this change enables runtime selection without code modifications.

### Update `auth.py` to read provider configuration

- **What**: Modify `Authenticator.__init__` to read `config.auth.provider` and instantiate the appropriate backend class.
- **Where**: `src/auth.py`, lines 24–31.
- **Why**: Decouples configuration from code, enabling new backends without touching the authenticator module.
```

## Atomicity Alignment

This format supports breakdown-tasks presentation while consuming the shared task
contract:

- **Single task result**: One H3 per drafted task result.
- **Result verification**: Attach checks to the drafted result using the shared contract.
- **Logical step pipeline**: H2 groups parallel steps; sequential H2s preserve
  operation order.
- **Dependent work serialization**: Separate H3s for multiple changes to the same file.
- **Skill-aware but not skill-bound**: The format describes work, not execution skills.

## Anti-Patterns to Avoid

- **Multiple changes per H3**: `### Refactor auth and add tests` — send the boundary
  back through the shared task-contract review.
- **Too many bullets**: More than 4 bullets per step indicates insufficient granularity
- **Vague "What"**: `### Update code` — lacks specificity; should name file and change type
- **Missing "Where"**: Bullet without file path or location makes diff inspection difficult

## Use Cases

- Implementation planning in task packets
- Change logs for configuration updates
- Migration documentation
- Feature specification in planning documents

## Related Docs

- [`core-rules.md`](./authoring/core-rules.md) — Operation procedures that consume
  the shared task contract
- [`task-granularity.md`](./authoring/task-granularity.md) — Boundary review guidance
- [`anti-patterns.md`](./authoring/anti-patterns.md) — Common mistakes and fixes
