---
name: skill-script-node-writer
description: "Use when generating deterministic TypeScript Node scripts from requirements, including CLI entry points, libraries, tests, and registration."
selection:
  role: owner
  tags:
    actions: [create Node script]
    inputs: [Node or TypeScript script requirements]
    outputs: [registered Node implementation]
    topics: [script implementation]
    environments: [Bun]
    constraints: [deterministic generation]
  use_when: [a TypeScript Node script and its project registration must be created]
  not_for: [adding tests to an existing Node script]
class: operation
---

# Generate TypeScript Node Scripts

## Normalize Input

Map invocation context to one internal input object.
Define these required fields:

- **Script name** — kebab-case entry point name (e.g., `lint-md`).
- **Purpose** — What the script computes or processes.
- **Input contract** — CLI arguments, stdin format, or file paths the script reads.
- **Output contract** — stdout format (JSON preferred), exit codes, stderr behavior.
- **Dependencies** — npm packages required (e.g., `cleye`, `remark`).
- **Skill consumers** — Which skills will invoke this script.

`BLOCKED: Missing script name — provide a kebab-case entry point name.`
`BLOCKED: Missing purpose — describe what the script computes or processes.`
`BLOCKED: Missing input contract — define CLI arguments, stdin format, or file paths.`

## Procedure

Each step is one imperative action.
Do not delegate sub-tasks.

1. **Parse requirements** — Extract script name, purpose, input/output contracts, dependencies, and skill consumers from the normalized input.
   Validate script name is kebab-case.
   Validate dependencies exist in `package.json` or add them.

2. **Select platform** — For general-purpose script requests outside this Node-specific operation, default to Python.
   Within this operation, choose Node only when the task requires Node-specific libraries (remark ecosystem, filesystem-heavy operations, or npm ecosystem tools).
   See [./reference/path-layout.md](./reference/path-layout.md) for platform selection context.

3. **Generate CLI entry point** — Write `src/cli/<script-name>.ts` with a cleye command definition, typed arguments and options, JSON stdout output via `process.stdout.write`, and error handling via `process.stderr.write` with `process.exit`.
   Follow conventions in [./reference/cli-conventions.md](./reference/cli-conventions.md).

4. **Generate lib modules** — Write `src/lib/<script-name>/core.ts` with typed function signatures, explicit return types, and imports from `lib/shared/*` where applicable.
   Follow conventions in [./reference/path-layout.md](./reference/path-layout.md).

5. **Register dependencies in package.json** — Add required npm packages under `dependencies` or `devDependencies`.
   Add a script entry under `"scripts"`: `<script-name> = "bun src/cli/<script-name>.ts"`.
   Follow conventions in [./reference/tooling-config.md](./reference/tooling-config.md).

6. **Ensure tooling config** — Create or update `biome.json` and `tsconfig.json` if absent.
   Follow conventions in [./reference/tooling-config.md](./reference/tooling-config.md).

7. **Run validation** — Execute type check, lint, and `--help` verification.
   Report `BLOCKED: <step> failed — <details>` on any failure.

## Self-Validation

Each check is a yes/no assertion.

- Type check passes — `bun run --cwd <scripts-node-dir> tsc --noEmit` exits zero.
- Lint passes — `bunx biome check src/cli/<script-name>.ts src/lib/<script-name>/` exits zero.
- Script `--help` works — `bun run --cwd <scripts-node-dir> <script-name> --help` exits zero.

## Expected Output

One or more files under `scripts/node/`:

- `src/cli/<script-name>.ts` — cleye CLI entry point with typed arguments, JSON output, and error handling.
- `src/lib/<script-name>/core.ts` — Core logic module with typed signatures.

`package.json` script entry registered under `"scripts"`.
`biome.json` and `tsconfig.json` present or updated.

## Shared Conventions

Load `skill-node-script-conventions` as passive documentation for authoritative shared
conventions. Apply the applicable cross-references below;
generated scripts must conform to their shared policies.

- **TypeScript/Node style** — `skill-node-script-conventions -> reference/typescript-node-style-guide.md`: Biome rules, strict-mode flags, import ordering, naming, type annotations, and coverage exemptions.
- **Shared libraries** — `skill-node-script-conventions -> reference/shared-lib-rules.md`, especially “Five Shared Module Rules”: shared-module entry-point, coverage, consumer documentation, naming, and extraction rules.
- **Paths and layout** — `skill-node-script-conventions -> reference/path-layout.md`, “Directory Layout (Both Roots),” “Import Conventions,” and “Module Organization Principles.” Keep this operation's platform decision above; the reference does not replace it.
- **Tooling and configuration** — `skill-node-script-conventions -> reference/tooling-config.md`, “Configure `biome.json`,” “Configure `tsconfig.json`,” and “Configure `package.json`.”
- **Bun tests** — `skill-node-script-conventions -> reference/bun-test-conventions.md`, “Naming Conventions,” “bun:test Globals,” “CLI Integration Tests with Bun.spawnSync,” “Fixture Setup Pattern (mkdtempSync / rmSync),” “Parameterized Tests,” “Test Isolation Conventions,” and “Mocking Patterns.”
- **Coverage** — `skill-node-script-conventions -> reference/coverage-strategy.md`, “Measurement Tool,” “Source Coverage Boundaries,” “Required Generated Suite Coverage And Recommended `fail_under = 100` Threshold,” “Edge Case Identification Checklist,” “Error Path Testing,” and “Coverage Exemption Conventions.”
- **Examples** — `skill-node-script-conventions -> reference/test-examples.md` provides complete CLI, unit, mocking, spy, parameterized, and fixture examples.

See the loaded `skill-node-script-conventions` entry point for the full reference inventory.

## Docs

See [./reference/README.md](./reference/README.md) for this skill's reference file index.
See `skill-node-script-conventions` (reference-README) for the shared conventions reference file index.
