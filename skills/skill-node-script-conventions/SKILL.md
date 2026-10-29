---
name: skill-node-script-conventions
description: "Use when referencing shared Node/TypeScript script conventions for OpenCode, including tooling, testing, and coverage."
selection:
  role: reference
  tags:
    inputs: [Node script requirements]
    outputs: [script convention guidance]
    topics: [Node TypeScript scripts]
    environments: [OpenCode]
    constraints: [Bun tooling]
  use_when: [Node or TypeScript script authoring needs shared conventions]
  not_for: [generating Node scripts or tests]
class: documentation
---

# Node Script Conventions

This documentation skill provides shared guidance for operation-class skills that author, review, or maintain Node/TypeScript scripts for OpenCode. It contains reference material only: it has no execution steps, side effects, or tool invocations. Downstream operation-class skills load it with the skill tool and refer to its files by relative path.

## Files

The following files reside under the `reference/` directory within this skill:

- **[`reference/typescript-node-style-guide.md`](reference/typescript-node-style-guide.md)** — TypeScript and Node.js coding style conventions including Biome lint rule catalog, strict-mode flag breakdown, import ordering convention, naming conventions, type annotation patterns, and coverage exemption conventions.
- **[`reference/shared-lib-rules.md`](reference/shared-lib-rules.md)** — Five rules for shared library modules under `src/lib/shared/`: no CLI entry points, 100% coverage requirement, consumer documentation in module-level JSDoc, domain-based naming, and extraction discipline (extract only when 2+ consumers).
- **[`reference/path-layout.md`](reference/path-layout.md)** — Directory and file path conventions for Node scripts — clean src/ layout, test layout, and import conventions. Defers platform selection and resolution order to skill-architect.
- **[`reference/tooling-config.md`](reference/tooling-config.md)** — Tooling configuration for `biome.json` (single quotes, semicolons asNeeded, indent 2, lineWidth 120), `tsconfig.json` (module: Preserve, types: [bun], strict flags), and `package.json` (bun deps, cleye). Defers resolution order to skill-architect.
- **[`reference/bun-test-conventions.md`](reference/bun-test-conventions.md)** — Conventions for `bun:test` test files: bun:test globals, Bun.spawnSync CLI test pattern, test file naming, mkdtempSync/rmSync fixture setup, test.each/describe.each parameterized tests, test isolation, paired source-to-test file mapping, mock.module() and spyOn() patterns.
- **[`reference/coverage-strategy.md`](reference/coverage-strategy.md)** — Coverage strategy for Bun tests: bun --coverage tooling, source path boundaries, threshold policy (100% fail_under), edge case identification checklist (6 categories), error path testing requiring Bun.spawnSync for every process.exit(code) path, and c8/@ts-expect-error exemption conventions.
- **[`reference/test-examples.md`](reference/test-examples.md)** — Complete runnable test examples: Bun.spawnSync CLI integration with temp fixture, mkdtempSync/rmSync file-based unit test, mock.module() module mocking, spyOn() spy, test.each parameterized input test, describe.each parameterized error-path test, and beforeAll shared fixture helper extraction pattern.
- **[`reference/README.md`](reference/README.md)** — Index of all reference files in this skill with one-sentence descriptions for quick navigation.
