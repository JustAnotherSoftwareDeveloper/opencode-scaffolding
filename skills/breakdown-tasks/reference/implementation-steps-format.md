# Implementation Steps Format

A structured format for documenting implementation steps using Markdown headers, subheaders, and 1-2 sentence bullets with selective bolding.

## Format Structure

The format uses a three-level Markdown hierarchy:

| Level | Purpose | Example |
|-------|---------|---------|
| **H2 Header** | Change category — groups related atomic changes | `## Authentication Refactoring` |
| **H3 Subheader** | Specific change — one atomic unit of work | `### Add `auth.provider` to `config.yaml` |
| **Bullets** | Details — 1-2 sentences with selective bolding | `- **What**: ...` |

## Format Rules

1. **One H3 per atomic change** — Each H3 subheader represents exactly one logical change (aligned with `Single Unit Of Work`)
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

This format supports the breakdown-tasks atomicity rules:

| Atomicity Rule | Format Implementation |
|----------------|----------------------|
| **Single Unit Of Work** | One H3 per logical change |
| **Single Output Artifact** | Each step produces one verifiable result |
| **Logical Step Pipeline** | H2 groups parallel steps; sequential H2s indicate dependencies |
| **Dependent Work Serialization** | Separate H3s for multiple changes to same file |
| **Skill-Aware But Not Skill-Bound** | Format describes work, not execution skills |

## Anti-Patterns to Avoid

- **Multiple changes per H3**: `### Refactor auth and add tests` — violates Single Unit Of Work
- **Too many bullets**: More than 4 bullets per step indicates insufficient granularity
- **Vague "What"**: `### Update code` — lacks specificity; should name file and change type
- **Missing "Where"**: Bullet without file path or location makes diff inspection difficult

## Use Cases

- Implementation planning in task packets
- Change logs for configuration updates
- Migration documentation
- Feature specification in planning documents

## Related Docs

- [`core-rules.md`](./core-rules.md) — Atomicity rules for task decomposition
- [`task-granularity.md`](./task-granularity.md) — Heuristics for splitting work
- [`anti-patterns.md`](./anti-patterns.md) — Common mistakes and fixes
