# Node Scripts

Node helpers are standalone from the root OpenCode package and are authored in TypeScript. Bun is the runtime and package-script runner for this workspace.

## Layout

- `src/`: executable TypeScript entry points.
- `lib/`: shared TypeScript modules imported by scripts in `src/`.

## Examples

Run package scripts with Bun:

```bash
bun run --cwd scripts/node example
```

Run a TypeScript entry point directly with Bun:

```bash
bun scripts/node/src/example.ts
```

The example script runs `src/example.ts`, which imports `lib/example.ts`.

This workspace intentionally avoids npm-specific scripts. If npm compatibility is needed later, add explicit fallback scripts and validation.
