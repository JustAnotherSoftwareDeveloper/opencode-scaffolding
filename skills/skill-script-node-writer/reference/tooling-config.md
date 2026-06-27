# Tooling Configuration

Every `scripts/node/` root must contain a `package.json`, `biome.json`, and `tsconfig.json`.
These files are generated or updated alongside each new script.

## biome.json

Biome enforces code formatting and lint rules.
Create or update `biome.json` at the `scripts/node/` root.

```json
{
  "$schema": "https://biomejs.dev/schemas/1.9.4/schema.json",
  "organizeImports": {
    "enabled": true
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true
    }
  },
  "formatter": {
    "enabled": true,
    "formatWithErrors": false,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 120
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "single",
      "semicolons": "asNeeded"
    }
  },
  "files": {
    "include": ["src/**/*.ts"],
    "ignore": ["node_modules", "bun.lock"]
  }
}
```

Invoke Biome: `bunx biome check src/` from the `scripts/node/` directory.

## tsconfig.json

TypeScript configuration for Bun-compatible compilation.

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "moduleDetection": "force",
    "allowImportingTsExtensions": true,
    "noEmit": true,
    "strict": true,
    "skipLibCheck": true,
    "noFallthroughCasesInSwitch": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "exactOptionalPropertyTypes": true,
    "noUncheckedIndexedAccess": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true
  },
  "include": ["src/**/*.ts"]
}
```

Key options:

- `"allowImportingTsExtensions": true` — enables `.ts` extension in import paths (Bun requirement).
- `"noEmit": true` — Bun handles compilation; no `tsc` output needed.
- `"moduleResolution": "bundler"` — matches Bun's module resolution semantics.
- `"verbatimModuleSyntax": true` — forces explicit `type` modifier on type-only imports.

Run type checking: `bun run --cwd <scripts-node-dir> tsc --noEmit`.

## package.json Script Entries

Each generated script gets a named entry under `"scripts"`.
The entry maps the script name to its CLI entry point.

```json
{
  "name": "scripts-node",
  "private": true,
  "type": "module",
  "packageManager": "bun@1.3.14",
  "scripts": {
    "<script-name>": "bun src/cli/<script-name>.ts"
  },
  "engines": {
    "bun": ">=1.3.14"
  },
  "dependencies": {
    "cleye": "^1.3.0"
  },
  "devDependencies": {
    "@types/node": "^26.0.1",
    "typescript": "^6.0.3",
    "biome": "^1.9.4"
  }
}
```

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

### Resolution Order

Scripts are resolved from two mandatory roots with an optional explicit override:

1. `$OPENCODE_SCRIPTS_NODE` — Environment variable explicit override (optional, highest priority).
2. `<project-root>/.opencode/scripts/node` — Project-local root (mandatory default, checked second).
3. `~/.config/opencode/scripts/node` — Global root (mandatory default, fallback).

**How skill origin determines root selection:**

- If the skill is loaded from a **project-local** skills directory, use `<project-root>/.opencode/scripts/node` as the primary root.
  Resolution falls through to the global root if a script or shared lib module is not found locally.
- If the skill is loaded from the **global** skills directory (`~/.config/opencode/skills/<name>/`), use `~/.config/opencode/scripts/node` as the primary root.

**Invocation pattern in skill steps:**

```shell
SCRIPTS_NODE="${OPENCODE_SCRIPTS_NODE:-$PWD/.opencode/scripts/node}"
SCRIPTS_NODE="${SCRIPTS_NODE:-$HOME/.config/opencode/scripts/node}"
bun run --cwd "$SCRIPTS_NODE" <script-name> [args]
```