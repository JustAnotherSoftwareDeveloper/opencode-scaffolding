# Path Layout

Generated Node scripts live under `scripts/node/` within either the global or project-local root.
Both roots follow the same directory layout; the difference is their filesystem location and resolution priority.

## Platform Selection: Node vs Python

Use Node scripts only when the task requires Node-specific capabilities:

- **remark ecosystem** — Markdown parsing, linting, and transformation.
- **Node filesystem APIs** — `node:fs`, `node:path`, `node:child_process` for operations where Python equivalents are less ergonomic.
- **npm ecosystem tools** — Libraries unavailable or poorly supported in Python.
- **Bun runtime features** — Built-in TypeScript execution, test runner, or package manager integration.

Default to Python (via `skill-script-python-writer`) for general-purpose scripting.
Node is the secondary platform, chosen when a capability gap makes Python impractical.

## Reference Content

For the full directory layout, import conventions, and shared lib patterns for `scripts/node/`, load `skill-node-script-conventions` (path-layout). This skill covers only the platform-selection guidance above; all other path/convention authority belongs to the shared conventions skill.
