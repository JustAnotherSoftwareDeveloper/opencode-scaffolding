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

# skill-maintenance-reference — Documentation Store

This skill is a passive data store for the current direct-selection maintenance
contract. It does not auto-read files when loaded.

## Documentation Files

Read the documentation files listed below as needed for your current task.
The bulleted list provides the mapping of files to their purpose.

- `reference/update-workflow.md` — Defines current-scope update workflow and content integrity rules.
- `reference/migration-guide.md` — Defines outright migration to the current profile.
- `reference/validation-checklist.md` — Lists shared-contract validation checks.
- `reference/gotchas.md` — Catalogues current profile maintenance pitfalls.

Choose the relevant files based on what you need to learn or reference.
Read only those files.
Do not read every file — read as needed.

## Docs

See the files under `./reference/` for the full reference documentation.
