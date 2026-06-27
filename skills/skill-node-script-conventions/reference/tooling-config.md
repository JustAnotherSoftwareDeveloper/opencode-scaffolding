# Tooling Configuration

Every `scripts/node/` root must contain a `package.json`, `biome.json`, and `tsconfig.json`.
These files are generated or updated alongside each new script.

> **Resolution order** — See `skill-architect` (platform-layout-context) for script-root resolution precedence (env var → project-local → global).
> **Path layout** — See `path-layout.md` for directory structure and import conventions.

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
    "include": ["src/**/*.ts", "tests/**/*.ts"],
    "ignore": ["node_modules", "bun.lock"]
  }
}
```

**Key options:**

- `organizeImports` — Auto-sort and merge imports into three groups (built-in, third-party, local).
- `javascript.formatter.quoteStyle` — Single quotes (`'single'`).
- `javascript.formatter.semicolons` — `"asNeeded"` (omit semicolons where ASI-safe).
- `include` — Both `src/**/*.ts` and `tests/**/*.ts` are formatted and linted.
- `ignore` — `node_modules` and `bun.lock` are excluded.

**Install:** `bun add -d -E @biomejs/biome` (pin version with `-E`).
**Invoke:** `bunx biome check src/` from the `scripts/node/` directory.

### Recommended Rules Reference

See `typescript-node-style-guide.md` > Biome Lint Rule Catalog for the full rule category breakdown.

## tsconfig.json

TypeScript configuration for Bun-compatible compilation.

```json
{
  "compilerOptions": {
    "lib": ["ESNext"],
    "target": "ESNext",
    "module": "Preserve",
    "moduleResolution": "bundler",
    "moduleDetection": "force",
    "allowImportingTsExtensions": true,
    "noEmit": true,
    "strict": true,
    "skipLibCheck": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "verbatimModuleSyntax": true,
    "exactOptionalPropertyTypes": true,
    "forceConsistentCasingInFileNames": true,
    "types": ["bun"]
  },
  "include": ["src/**/*.ts", "tests/**/*.ts"]
}
```

**Key options:**

- `module` set to `"Preserve"` — Bun recommends this over `"ESNext"`; it preserves ESM syntax for Bun's runtime
- `moduleResolution` set to `"bundler"` — Matches Bun's module resolution semantics
- `allowImportingTsExtensions` set to `true` — Required to use `.ts` extension in import paths (Bun requirement)
- `noEmit` set to `true` — Bun handles compilation directly; no `tsc` output needed
- `strict` set to `true` — Enables the full suite of strict type-checking options
- `types` set to `["bun"]` — Provides Bun's built-in API types (`Bun` global, `Bun.spawnSync`, etc.)
- `verbatimModuleSyntax` set to `true` — Forces explicit `type` modifier on type-only imports

**Run type checking:** `bun run --cwd <scripts-node-dir> tsc --noEmit`.

## package.json

```json
{
  "name": "scripts-node",
  "private": true,
  "type": "module",
  "packageManager": "bun@1.3.14",
  "scripts": {
    "<script-name>": "bun src/cli/<script-name>.ts",
    "test": "bun test",
    "test:<script-name>": "bun test tests/<script-name>.test.ts",
    "test:<script-name>:cli": "bun test tests/<script-name>.cli.test.ts"
  },
  "engines": {
    "bun": ">=1.3.14"
  },
  "dependencies": {
    "cleye": "^1.3.0"
  },
  "devDependencies": {
    "@types/bun": "^1.3.0",
    "@types/node": "^26.0.1",
    "typescript": "^6.0.3",
    "@biomejs/biome": "^1.9.4"
  }
}
```

### Key Conventions

- `"type": "module"` — Required for ESM imports.
- `"packageManager"` — Pin to `bun` for consistency across environments.
- **Script entries** — Map each script to `bun src/cli/<name>.ts`. Test scripts use `bun test` with file filters.
- **`cleye`** — Required dependency for all CLI scripts.
- **`@types/bun`** — Provides types for Bun-specific APIs (`Bun.spawnSync`, etc.).
- **`@types/node`** — Provides types for Node.js built-in APIs.
- **`typescript`** — Required for `tsc --noEmit` type checking.
- **`@biomejs/biome`** — Replaces ESLint + Prettier.

### Script Naming Convention

Script names use kebab-case matching the entry point file name.
The script name becomes both the directory name under `src/lib/` and the `package.json` key.

Example: A script named `lint-md` produces:

- `"scripts": { "lint:md": "bun src/cli/lint-md.ts" }`
- `src/lib/lint-md/core.ts`

### Dependency Installation Commands

```bash
# Core dependencies
bun add cleye@^1.3.0

# Dev dependencies
bun add -d @types/bun@^1.3.0 @types/node@^26.0.1 typescript@^6.0.3
bun add -d -E @biomejs/biome
```
