# Tooling Configuration

## Writer-Specific Additions

### Script Naming Convention

Script names use kebab-case matching the entry point file name.
The script name becomes both the directory name under `src/lib/` and the `package.json` key.

Example: A script named `lint-md` produces:

- `"scripts": { "lint:md": "bun src/cli/lint-md.ts" }`
- `src/lib/lint-md/core.ts`

### Standard Dependencies

- `cleye` — Required for every CLI script.
- `@types/node` — Required for every script (dev dependency).
- `typescript` — Required for every script (dev dependency).
- `remark` — Required for Markdown processing.
- `remark-gfm` — Required for GitHub-Flavored Markdown.
- `remark-lint` — Required for Markdown linting.

## Reference Content

For shared tooling configuration (`biome.json`, `tsconfig.json`, `package.json` conventions), load `skill-node-script-conventions` (tooling-config).

For resolution order and script-root precedence, load `skill-architect` (platform-layout-context).
