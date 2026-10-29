---
name: skill-maintenance-reference
description: "Use when referencing maintenance workflows, migration procedures, validation checks, or known pitfalls for skill maintenance."
selection:
  role: reference
  tags:
    topics:
      - skill maintenance
    outputs:
      - maintenance guidance
    constraints:
      - migration validation
  use_when:
    - maintaining or migrating an existing skill workspace
  not_for:
    - creating or updating skill implementation files
class: documentation
---

# Maintenance Reference

This skill is a passive data store for the current direct-selection maintenance
contract. It does not auto-read files when loaded.

## Documentation Files

Read only the files relevant to your task. Use the descriptions below to choose which
references to consult.

- [Update workflow](reference/update-workflow.md) — Defines current-scope update workflow and content integrity rules.
- [Migration guide](reference/migration-guide.md) — Defines outright migration to the current profile.
- [Validation checklist](reference/validation-checklist.md) — Lists shared-contract validation checks.
- [Gotchas](reference/gotchas.md) — Catalogues current profile maintenance pitfalls.

## Docs

See the files under `./reference/` for the full reference documentation.
