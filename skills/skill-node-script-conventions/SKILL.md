---
name: skill-node-script-conventions
description: Use when writing or maintaining Node/TypeScript scripts for the OpenCode platform and needing convention guidance on style, shared library rules, path layout, tooling, testing, and coverage.
schema_version: "1.0"
cues:
  - {facet: subject, value: "Node TypeScript scripts"}
  - {facet: environment, value: "OpenCode"}
  - {facet: outcome, value: "script convention guidance"}
  - {facet: constraint, value: "Bun tooling"}
relationships:
  - {role: reference, rationale: "provides passive Node script conventions"}
class: documentation
---

# Node Script Conventions

This skill holds shared reference documentation consumed by other skills when authoring, reviewing, or maintaining Node/TypeScript scripts for the OpenCode platform. It is a passive data store with no execution steps, no side effects, and no tool invocations. Downstream operation-class skills load this skill via the skill tool and reference its files by relative path.

## Files

The following files reside under the `reference/` directory within this skill:

- **`reference/typescript-node-style-guide.md`** — TypeScript and Node.js coding style conventions including Biome lint rule catalog, strict-mode flag breakdown, import ordering convention, naming conventions table, type annotation patterns, and coverage exemption conventions.
- **`reference/shared-lib-rules.md`** — Five rules for shared library modules under `src/lib/shared/`: no CLI entry points, 100% coverage requirement, consumer documentation in module-level JSDoc, domain-based naming, and extraction discipline (extract only when 2+ consumers).
- **`reference/path-layout.md`** — Directory and file path conventions for Node scripts — clean src/ layout, test layout, and import conventions. Defers platform selection and resolution order to skill-architect.
- **`reference/tooling-config.md`** — Tooling configuration for `biome.json` (single quotes, semicolons asNeeded, indent 2, lineWidth 120), `tsconfig.json` (module: Preserve, types: [bun], strict flags), and `package.json` (bun deps, cleye). Defers resolution order to skill-architect.
- **`reference/bun-test-conventions.md`** — Conventions for `bun:test` test files: bun:test globals, Bun.spawnSync CLI test pattern, test file naming, mkdtempSync/rmSync fixture setup, test.each/describe.each parameterized tests, test isolation, paired source-to-test file mapping, mock.module() and spyOn() patterns.
- **`reference/coverage-strategy.md`** — Coverage strategy for Bun tests: bun --coverage tooling, source path boundaries, threshold policy (100% fail_under), edge case identification checklist (6 categories), error path testing requiring Bun.spawnSync for every process.exit(code) path, and c8/@ts-expect-error exemption conventions.
- **`reference/test-examples.md`** — Complete runnable test examples: Bun.spawnSync CLI integration with temp fixture, mkdtempSync/rmSync file-based unit test, mock.module() module mocking, spyOn() spy, test.each parameterized input test, describe.each parameterized error-path test, and beforeAll shared fixture helper extraction pattern.
- **`reference/README.md`** — Index of all reference files in this skill with one-sentence descriptions for quick navigation.
